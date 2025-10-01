"""
Input sanitization utilities for text fields to prevent XSS and other attacks.
Uses bleach library to clean HTML and prevent script injection.
"""

import bleach
from django.conf import settings


# Define allowed HTML tags and attributes for different field types
ALLOWED_TAGS = {
    'basic': [],  # No HTML tags allowed
    'rich_text': ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li'],  # Basic formatting
    'notes': ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'blockquote'],  # Extended formatting
}

ALLOWED_ATTRIBUTES = {
    'basic': {},
    'rich_text': {},
    'notes': {},
}


def sanitize_html(text, field_type='basic'):
    """
    Sanitize HTML content to prevent XSS attacks.

    Args:
        text: The text to sanitize
        field_type: Type of field ('basic', 'rich_text', 'notes')

    Returns:
        Sanitized text with dangerous HTML removed
    """
    if not text:
        return text

    # Get allowed tags and attributes for field type
    allowed_tags = ALLOWED_TAGS.get(field_type, [])
    allowed_attributes = ALLOWED_ATTRIBUTES.get(field_type, {})

    # Clean the text using bleach
    cleaned_text = bleach.clean(
        text,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True,  # Strip disallowed tags instead of escaping
        strip_comments=True  # Remove HTML comments
    )

    return cleaned_text


def sanitize_field(instance, field_name, field_type='basic'):
    """
    Sanitize a specific field on a model instance.

    Args:
        instance: Model instance
        field_name: Name of the field to sanitize
        field_type: Type of field for sanitization rules
    """
    value = getattr(instance, field_name, None)
    if value:
        sanitized_value = sanitize_html(value, field_type)
        setattr(instance, field_name, sanitized_value)


def sanitize_model_fields(instance, fields_config):
    """
    Sanitize multiple fields on a model instance.

    Args:
        instance: Model instance
        fields_config: Dictionary mapping field names to field types
                      e.g., {'notes': 'notes', 'medical_notes': 'basic'}
    """
    for field_name, field_type in fields_config.items():
        sanitize_field(instance, field_name, field_type)