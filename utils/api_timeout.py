import requests


def safe_api_call(method, url, **kwargs):
    timeout = kwargs.pop("timeout", 10)  # Default 10s
    try:
        response = requests.request(method, url, timeout=timeout, **kwargs)
        response.raise_for_status()
        return response
    except requests.Timeout:
        return {"error": "Request timed out"}, 504
    except requests.RequestException as e:
        return {"error": str(e)}, 502
