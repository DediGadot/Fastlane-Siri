#!/usr/bin/env python3
"""
AWS Lambda handler for Fast Lane price service
"""
import json
import logging
import os
import time
from datetime import datetime, timedelta
import boto3
import requests
from scraper import extract_price, validate_price

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize AWS services
dynamodb = boto3.resource('dynamodb')
CACHE_TABLE = os.environ.get('CACHE_TABLE', 'fastlane-price-cache')

def get_cached_price():
    """Get price from DynamoDB cache"""
    try:
        table = dynamodb.Table(CACHE_TABLE)
        response = table.get_item(Key={'id': 'current_price'})
        
        if 'Item' in response:
            item = response['Item']
            # Check if cache is still valid (5 minutes)
            cache_time = datetime.fromisoformat(item['timestamp'])
            if datetime.now() - cache_time < timedelta(minutes=5):
                logger.info("Cache hit - returning cached price")
                return item['price']
        
        logger.info("Cache miss or expired")
        return None
        
    except Exception as e:
        logger.error(f"Cache read error: {e}")
        return None

def cache_price(price):
    """Store price in DynamoDB cache"""
    try:
        table = dynamodb.Table(CACHE_TABLE)
        # TTL for automatic cleanup after 1 hour
        ttl = int(time.time()) + 3600
        
        table.put_item(Item={
            'id': 'current_price',
            'price': price,
            'timestamp': datetime.now().isoformat(),
            'ttl': ttl
        })
        logger.info(f"Cached price: {price}")
        
    except Exception as e:
        logger.error(f"Cache write error: {e}")

def fetch_fresh_price():
    """Fetch price from fastlane.co.il"""
    try:
        logger.info("Fetching fresh price from fastlane.co.il")
        response = requests.get(
            'https://fastlane.co.il/',
            timeout=10,
            headers={
                'User-Agent': 'Mozilla/5.0 (compatible; FastLane-Price-Bot/1.0)'
            }
        )
        response.raise_for_status()
        
        price = extract_price(response.text)
        if validate_price(price):
            cache_price(price)
            return price
        else:
            logger.error("Invalid price extracted")
            return None
            
    except requests.RequestException as e:
        logger.error(f"Network error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None

def create_response(status_code, body, cached=False):
    """Create standardized API response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Cache-Control': 'public, max-age=300'  # 5 minutes
        },
        'body': json.dumps(body)
    }

def main(event, context):
    """
    Main Lambda handler
    
    Returns JSON with:
    - price: int (NIS)
    - cached: bool
    - text_he: str (Hebrew)
    - text_en: str (English)
    """
    logger.info(f"Request from {event.get('requestContext', {}).get('identity', {}).get('sourceIp', 'unknown')}")
    
    try:
        # Try cache first
        price = get_cached_price()
        cached = price is not None
        
        # If no cached price, fetch fresh
        if price is None:
            price = fetch_fresh_price()
            
        if price is None:
            return create_response(503, {
                'error': 'Service temporarily unavailable',
                'message': 'Could not retrieve current price'
            })
        
        # Success response
        response_body = {
            'price': price,
            'cached': cached,
            'timestamp': datetime.now().isoformat(),
            'text_he': f"המחיר בנתיב המהיר כעת: {price} שקלים",
            'text_en': f"Fast lane toll price: {price} shekels",
            'currency': 'ILS'
        }
        
        return create_response(200, response_body, cached)
        
    except Exception as e:
        logger.error(f"Handler error: {e}")
        return create_response(500, {
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        })

# Health check endpoint
def health(event, context):
    """Health check handler"""
    return create_response(200, {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })