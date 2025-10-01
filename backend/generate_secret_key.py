#!/usr/bin/env python
"""
Generate a secure Django SECRET_KEY
"""

import logging
import sys
from django.core.management.utils import get_random_secret_key

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def main():
    secret_key = get_random_secret_key()

    # Use logging instead of print for better practice
    logger.info("\n" + "="*60)
    logger.info("DJANGO SECRET KEY GENERATOR")
    logger.info("="*60)
    logger.info("\nYour new secret key is:")
    logger.info("-"*60)
    logger.info(secret_key)
    logger.info("-"*60)
    logger.info("\n⚠️  IMPORTANT:")
    logger.info("1. Add this to your .env file as: SECRET_KEY=<your-key>")
    logger.info("2. NEVER commit this key to version control")
    logger.info("3. Keep this key secret and secure")
    logger.info("4. Use different keys for development and production")
    logger.info("5. Consider also generating a JWT_SECRET_KEY for JWT tokens")
    logger.info("="*60 + "\n")

    # Also generate a JWT secret key
    jwt_key = get_random_secret_key()
    logger.info("Optional JWT_SECRET_KEY:")
    logger.info("-"*60)
    logger.info(jwt_key)
    logger.info("-"*60 + "\n")

if __name__ == "__main__":
    main()