# Enhanced AI-Powered Customer Input Parsing System

## Overview

This system replaces the basic customer data parsing in `utils.py` with an advanced AI-enhanced version that can:

- **Parse natural language input** like "John Doe lives at 123 Main St, email john@example.com, phone 555-1234"
- **Use Hugging Face NER models** for intelligent entity recognition
- **Handle multiple data formats** including comma-separated, tab-separated, and unstructured text
- **Auto-correct common mistakes** in addresses, phone numbers, and contact information
- **Provide confidence scoring** and data quality assessment
- **Gracefully fallback** to traditional parsing if AI models fail

## Installation

### 1. Install Dependencies

```bash
# Install AI/ML dependencies
pip install torch>=2.0.0 transformers>=4.30.0 tokenizers>=0.13.0

# Or install from requirements.txt (already updated)
pip install -r requirements.txt
```

### 2. Optional: Set Environment Variables

```bash
# Optional: Set Hugging Face token for private models
export HUGGINGFACE_TOKEN="your_hf_token_here"

# Optional: Force CPU-only mode (useful for production with limited GPU)
export AI_PARSER_CPU_ONLY=1

# Optional: Override default model
export AI_PARSER_MODEL="dbmdz/bert-base-cased-finetuned-conll03-english"

# Optional: Set minimum confidence threshold
export AI_PARSER_MIN_CONFIDENCE=0.7
```

## Quick Start

### Basic Usage

```python
from utils import parse_customer_input, normalize_customer_data

# Parse natural language input
input_text = "John Doe lives at 123 Main Street, Springfield, IL 62704, email john.doe@example.com, phone +1-555-123-4567"

# Parse the input
result = parse_customer_input(input_text)

# Normalize and clean the data
if result:
    clean_data = normalize_customer_data(result)
    print(f"Name: {clean_data['name']}")
    print(f"Phone: {clean_data['phone']}")
    print(f"Email: {clean_data['email']}")
    print(f"Address: {clean_data['address_1']}")
    print(f"Confidence: {clean_data.get('confidence', 0):.2f}")
    print(f"Quality Score: {clean_data.get('data_quality_score', 0):.2f}")
```

### Flask Integration

```python
from flask import Flask, request, jsonify
from utils import parse_customer_input, normalize_customer_data

app = Flask(__name__)

@app.route('/parse-customer', methods=['POST'])
def parse_customer():
    try:
        input_text = request.json.get('customer_input', '')
        
        # Parse the customer input
        result = parse_customer_input(input_text)
        
        if result:
            # Normalize the data
            normalized = normalize_customer_data(result)
            
            return jsonify({
                'success': True,
                'data': normalized,
                'parsing_method': normalized.get('detected_format'),
                'confidence': normalized.get('confidence', 0),
                'quality_score': normalized.get('data_quality_score', 0),
                'suggestions': normalized.get('validation_suggestions', [])
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Could not parse customer information'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

## Testing

### Run the Test Suite

```bash
# Test the enhanced parsing system
python test_enhanced_parsing.py

# Run integration examples
python example_integration.py
```

### Example Test Cases

The system can handle various input formats:

1. **Natural Language**: "John Doe lives at 123 Main St, email john@example.com, phone 555-1234"
2. **Informal Format**: "Sarah - call me at (555) 987-6543 or email sarah@gmail.com - I'm at 456 Oak Ave, Chicago"
3. **International**: "Emma Wilson, +44 20 7946 0958, emma@uk.co.uk, 10 Downing Street, London SW1A 2AA"
4. **Traditional CSV**: "Alice Brown,321 Cedar Dr,Miami,FL,33101,alice@email.com,305-555-0123"
5. **Tab-separated**: "Bob Smith\t555-555-5555 bob@test.com\t123 Elm St\t\tDallas\tTX\t75201\tUS"

## Configuration

### AI Model Configuration (`ai_config.py`)

```python
# Primary NER model (high accuracy)
PRIMARY_NER_MODEL = "dbmdz/bert-large-cased-finetuned-conll03-english"

# Fallback models (faster, smaller)
FALLBACK_NER_MODELS = [
    "dbmdz/bert-base-cased-finetuned-conll03-english",
    "mdarhri00/named-entity-recognition"
]

# Performance settings
PERFORMANCE_CONFIG = {
    "enable_caching": True,
    "timeout_seconds": 30,
}

# Parsing thresholds
PARSING_THRESHOLDS = {
    "min_confidence": 0.6,  # Minimum confidence to use AI results
    "fallback_to_traditional": True
}
```

### Environment Overrides

- `AI_PARSER_MODEL`: Override the primary model
- `AI_PARSER_MIN_CONFIDENCE`: Set minimum confidence threshold
- `AI_PARSER_CPU_ONLY`: Force CPU-only processing
- `HUGGINGFACE_TOKEN`: Authentication for private models

## Features

### 1. AI-Enhanced Entity Recognition

Uses state-of-the-art BERT models fine-tuned on Named Entity Recognition tasks to identify:
- Person names (PER)
- Locations (LOC) 
- Organizations (ORG)
- Miscellaneous entities (MISC)

### 2. Advanced Pattern Recognition

Enhanced regex patterns for:
- **Phone Numbers**: Multiple international formats, extensions, various separators
- **Email Addresses**: Comprehensive validation and extraction
- **Postal Codes**: US, Canada, UK, Germany, and other formats
- **Addresses**: Street addresses with numbers, names, and directional indicators

### 3. Auto-Correction Features

Automatically corrects common mistakes:
- State name standardization (e.g., "California" → "CA")
- Phone number formatting (e.g., "5551234567" → "+1-555-123-4567")
- Email case normalization
- Name title case formatting

### 4. Data Quality Assessment

Provides comprehensive data quality metrics:
- **Completeness Score**: Based on required field presence
- **Format Validation**: Validates phone, email, postal code formats
- **Confidence Scoring**: AI model confidence in extracted entities
- **Validation Suggestions**: Actionable recommendations for data improvement

### 5. Backward Compatibility

- All existing parsing functions continue to work
- Traditional parsing methods serve as fallbacks
- API remains unchanged for existing integrations
- Graceful degradation when AI models unavailable

## Performance Considerations

### Model Loading

- Models are loaded once and cached globally
- First parsing request may be slower due to model initialization
- Subsequent requests are fast (typically <100ms)

### Memory Usage

- BERT-large model: ~1.3GB GPU/RAM
- BERT-base model: ~400MB GPU/RAM  
- CPU-only mode uses less memory but is slower

### Production Recommendations

1. **Use GPU acceleration** when available for better performance
2. **Pre-warm models** during application startup
3. **Monitor memory usage** with large models
4. **Set appropriate timeouts** for model loading
5. **Use fallback models** for resource-constrained environments

```python
# Example pre-warming during app startup
from utils import get_ner_pipeline

def initialize_ai_models():
    """Pre-load AI models during application startup"""
    try:
        pipeline = get_ner_pipeline()
        if pipeline:
            # Warm up with a dummy input
            pipeline("John Doe")
            print("✅ AI models loaded successfully")
    except Exception as e:
        print(f"⚠️ AI model initialization failed: {e}")

# Call during Flask app initialization
initialize_ai_models()
```

## Troubleshooting

### Common Issues

1. **Model Loading Failures**
   - Check internet connection
   - Verify disk space (models are ~400MB-1.3GB)
   - Try fallback models or CPU-only mode

2. **CUDA Out of Memory**
   - Set `AI_PARSER_CPU_ONLY=1`
   - Use smaller base model instead of large model
   - Reduce batch size in configuration

3. **Slow Performance**
   - Enable GPU acceleration
   - Use model caching
   - Pre-warm models during startup

4. **Parsing Accuracy Issues**
   - Lower confidence threshold
   - Enable traditional parsing fallback
   - Check input text quality and format

### Debug Mode

Enable detailed logging:

```python
import logging
logging.getLogger('utils').setLevel(logging.DEBUG)
```

## Security Considerations

1. **Model Source**: All models are from verified Hugging Face repositories
2. **Data Privacy**: Customer data is processed locally, not sent to external APIs
3. **Input Validation**: All inputs are sanitized and validated
4. **Error Handling**: Comprehensive error handling prevents crashes

## Migration from Existing System

The enhanced parsing system is designed to be a drop-in replacement:

### Before (Old System)
```python
result = parse_customer_input(input_text)
```

### After (Enhanced System)
```python
result = parse_customer_input(input_text)  # Same API!
# Now includes AI features, confidence scores, and quality assessment
```

### Additional Features Available
```python
# Get enhanced contact extraction
contact_info = extract_contact_info(input_text)

# Get data quality assessment
normalized = normalize_customer_data(result)
quality_score = normalized.get('data_quality_score')
suggestions = normalized.get('validation_suggestions')
```

## Deployment Checklist

- [ ] Install dependencies: `pip install torch transformers tokenizers`
- [ ] Test with sample data: `python test_enhanced_parsing.py`
- [ ] Configure models in `ai_config.py`
- [ ] Set environment variables for production
- [ ] Pre-warm models during application startup
- [ ] Monitor performance and memory usage
- [ ] Set up logging for debugging
- [ ] Test fallback behavior when AI models fail
- [ ] Validate with real customer data
- [ ] Update existing integrations to use new features

## Support

For issues or questions:
1. Check the troubleshooting section
2. Run the test suite to verify functionality
3. Review logs for error details
4. Test with simplified inputs to isolate issues

The system provides comprehensive logging and error handling to help diagnose issues quickly.