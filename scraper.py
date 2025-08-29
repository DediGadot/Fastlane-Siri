#!/usr/bin/env python3
"""
Fast Lane price scraper - does one thing well
"""
import re
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def extract_price(html_content):
    """
    Extract price from FastLane HTML content
    
    Args:
        html_content (str): Raw HTML from fastlane.co.il
        
    Returns:
        int: Price in NIS, or None if not found
    """
    if not html_content:
        return None
        
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text()
        
        # Multiple regex patterns to catch the price
        patterns = [
            r'(\d+)\s*₪',              # "8 ₪"
            r'₪\s*(\d+)',              # "₪ 8"  
            r'המחיר\s+עכשיו\s+(\d+)',    # "המחיר עכשיו 8"
            r'המחיר\s+כעת\s+(\d+)',     # "המחיר כעת 8"
            r'המחיר.*?(\d+)\s*₪',       # "המחיר ... 8 ₪"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.UNICODE)
            if match:
                price = int(match.group(1))
                # Sanity check - Fast Lane prices should be reasonable
                if 1 <= price <= 100:
                    logger.info(f"Extracted price: {price} NIS")
                    return price
                else:
                    logger.warning(f"Price {price} seems unreasonable, skipping")
                    
        logger.warning("No price found in HTML content")
        return None
        
    except Exception as e:
        logger.error(f"Error extracting price: {e}")
        return None

def validate_price(price):
    """Validate extracted price is sane"""
    return price and isinstance(price, int) and 1 <= price <= 100