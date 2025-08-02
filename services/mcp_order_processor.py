"""
Module for processing orders using MCP (Model Control Plane) services.
Handles NER, address parsing, text classification, and intent detection.
"""

import logging
import time
import requests


class MCPOrderProcessor:
    """
    Processor for interacting with MCP endpoints for order parsing, classification,
    and validation of order data.
    """

    def __init__(self, mcp_url=None, timeout=10, max_retries=3):
        """Initialize MCP processor with optional Hugging Face Pro token support."""
        import os

        if mcp_url is None:
            mcp_url = os.environ.get("MCP_URL", "http://localhost:3000")
        self.mcp_url = mcp_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = logging.getLogger(__name__)

        # Hugging Face Pro token support
        hf_token = os.environ.get("HF_TOKEN")
        self.headers = {"Content-Type": "application/json"}
        if hf_token:
            self.headers["Authorization"] = f"Bearer {hf_token}"

    def health_check(self):
        """Check MCP server health."""
        try:
            resp = requests.get(f"{self.mcp_url}/health", timeout=3)
            if resp.status_code == 200:
                return True
            self.logger.warning(
                "MCP health check failed: %s %s", resp.status_code, resp.text
            )
            return False
        except Exception as e:
            self.logger.error(f"Health check exception: {e}")
            return False

    def _post_with_retry(self, endpoint, payload):
        """POST with retry and exponential backoff."""
        url = f"{self.mcp_url}{endpoint}"
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = requests.post(
                    url,
                    json=payload,
                    headers=self.headers,
                    timeout=self.timeout,
                )
                resp.raise_for_status()
                return resp.json()
            except requests.exceptions.Timeout:
                self.logger.warning(f"Timeout on {url} (attempt {attempt})")
            except requests.exceptions.ConnectionError as e:
                self.logger.warning(
                    f"Connection error on {url} (attempt {attempt}): {e}"
                )
            except requests.exceptions.HTTPError as e:
                self.logger.error(
                    f"HTTP error on {url}: {e} - {getattr(e.response, 'text', '')}"
                )
                break  # Don't retry on HTTP errors
            except Exception as e:
                self.logger.error(f"Unexpected error on {url}: {e}")
            time.sleep(2**attempt)
        self.logger.error(
            f"Failed to POST to {url} after {self.max_retries} attempts."
        )
        return None

    def run_ner(self, text):
        """Named Entity Recognition. Returns None on failure."""
        endpoint = "/tools/ner/infer"
        payload = {"inputs": text}
        result = self._post_with_retry(endpoint, payload)
        if result is None:
            self.logger.error("NER failed, returning empty result.")
            return []
        return result

    def run_address_parser(self, text):
        """Address parsing. Returns None on failure."""
        endpoint = "/tools/address-parser/infer"
        payload = {"inputs": text}
        result = self._post_with_retry(endpoint, payload)
        if result is None:
            self.logger.error("Address parsing failed, returning empty result.")
            return {}
        return result

    def run_text_classification(self, text):
        """Text classification for routing. Returns None on failure."""
        endpoint = "/tools/text-classification/infer"
        payload = {"inputs": text}
        result = self._post_with_retry(endpoint, payload)
        if result is None:
            self.logger.error("Text classification failed, returning empty result.")
            return {}
        return result

    def run_intent_detection(self, text):
        """Detect order intent. Returns None on failure."""
        endpoint = "/tools/intent-detection/infer"
        payload = {"inputs": text}
        result = self._post_with_retry(endpoint, payload)
        if result is None:
            self.logger.error("Intent detection failed, returning empty result.")
            return {}
        return result

    def process_order(self, raw_text):
        """Main entry: parse, classify, and validate order input. Adds error and fallback handling."""
        errors = []
        if not self.health_check():
            errors.append("MCP server unavailable. Fallback mode activated.")
            self.logger.error(
                "MCP server unavailable. All results will be empty/fallback."
            )
            return {
                "entities": [],
                "address": {},
                "routing": {},
                "intent": {},
                "confidence": 0.0,
                "manual_review": True,
                "errors": errors,
            }

        entities = self.run_ner(raw_text)
        address = self.run_address_parser(raw_text)
        routing = self.run_text_classification(raw_text)
        intent = self.run_intent_detection(raw_text)

        confidence = self._calculate_confidence(entities, address, routing, intent)

        return {
            "entities": entities,
            "address": address,
            "routing": routing,
            "intent": intent,
            "confidence": confidence,
            "manual_review": confidence < 0.8,
            "errors": errors,
        }

    def _calculate_confidence(self, entities, address, routing, intent):
        """Calculate confidence score based on parsed results."""
        score = 0.0
        if entities:
            score += 0.25
        if address:
            score += 0.25
        if routing:
            score += 0.25
        if intent:
            score += 0.25
        return score

    def debug_mcp_connectivity(self):
        """Utility: test all MCP endpoints and print results."""
        test_text = "John Doe, 123 Main St, Las Vegas, NV 89101"
        print("MCP Health:", self.health_check())
        print("NER:", self.run_ner(test_text))
        print("Address Parse:", self.run_address_parser(test_text))
        print("Text Classification:", self.run_text_classification(test_text))
        print("Intent Detection:", self.run_intent_detection(test_text))
