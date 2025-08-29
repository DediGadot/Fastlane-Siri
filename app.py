#!/usr/bin/env python3
"""
Fast Lane Price Service - Local Edition
No cloud garbage, just Python serving HTTP
"""
from flask import Flask, jsonify, request
import sqlite3
import logging
from datetime import datetime, timedelta
import requests
from scraper import extract_price

app = Flask(__name__)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = '/tmp/fastlane.db'

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS cache 
                    (key TEXT PRIMARY KEY, value INTEGER, timestamp TEXT)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS requests 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                     ip TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()
    logger.info(f"Database initialized at {DB_PATH}")

def get_cached_price():
    """Get price from cache if still valid (5 minutes)"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT value, timestamp FROM cache WHERE key='price'")
        row = c.fetchone()
        conn.close()
        
        if row:
            cache_time = datetime.fromisoformat(row[1])
            age_seconds = (datetime.now() - cache_time).total_seconds()
            if age_seconds < 300:  # 5 minutes
                logger.info(f"Cache hit - price {row[0]} is {age_seconds:.0f}s old")
                return row[0]
            else:
                logger.info(f"Cache expired - {age_seconds:.0f}s old")
        
        return None
    except Exception as e:
        logger.error(f"Cache read error: {e}")
        return None

def save_price(price):
    """Save price to cache"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT OR REPLACE INTO cache VALUES (?, ?, ?)",
                     ('price', price, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        logger.info(f"Cached price: {price} NIS")
    except Exception as e:
        logger.error(f"Cache write error: {e}")

def log_request():
    """Log incoming requests"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO requests VALUES (NULL, ?, ?)",
                     (request.remote_addr, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    except:
        pass  # Don't fail on logging errors

@app.route('/price')
def get_price():
    """Get current Fast Lane price"""
    log_request()
    client_ip = request.remote_addr
    logger.info(f"Price request from {client_ip}")
    
    # Try cache first
    price = get_cached_price()
    cached = price is not None
    
    # Fetch fresh if no cache
    if price is None:
        try:
            logger.info("Fetching fresh price from fastlane.co.il")
            response = requests.get(
                'https://fastlane.co.il/',
                timeout=10,
                headers={'User-Agent': 'Mozilla/5.0 (FastLane-Price-Service/1.0)'}
            )
            response.raise_for_status()
            
            price = extract_price(response.text)
            if price:
                save_price(price)
                logger.info(f"Fresh price fetched: {price} NIS")
            else:
                logger.error("Could not extract price from website")
                
        except requests.RequestException as e:
            logger.error(f"Network error fetching price: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
    
    # Return response
    if price:
        return jsonify({
            'price': price,
            'cached': cached,
            'timestamp': datetime.now().isoformat(),
            'text_he': f'המחיר בנתיב המהיר: {price} שקלים',
            'text_en': f'Fast lane toll price: {price} shekels',
            'currency': 'ILS'
        })
    else:
        return jsonify({
            'error': 'Service temporarily unavailable',
            'message': 'Could not retrieve current price'
        }), 503

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'fastlane-price-local'
    })

@app.route('/')
def root():
    """Root endpoint"""
    return jsonify({
        'service': 'Fast Lane Price Service',
        'version': '1.0-local',
        'endpoints': {
            '/price': 'Get current toll price',
            '/health': 'Health check'
        }
    })

@app.route('/stats')
def stats():
    """Simple stats endpoint"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Get request count today
        today = datetime.now().date().isoformat()
        c.execute("SELECT COUNT(*) FROM requests WHERE date(timestamp) = ?", (today,))
        requests_today = c.fetchone()[0]
        
        # Get cache info
        c.execute("SELECT value, timestamp FROM cache WHERE key='price'")
        cache_row = c.fetchone()
        
        conn.close()
        
        cache_info = None
        if cache_row:
            cache_age = (datetime.now() - datetime.fromisoformat(cache_row[1])).total_seconds()
            cache_info = {
                'price': cache_row[0],
                'age_seconds': int(cache_age),
                'valid': cache_age < 300
            }
        
        return jsonify({
            'requests_today': requests_today,
            'cache': cache_info,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    print("Starting Fast Lane service on port 8080...")
    print("Access at: http://localhost:8080/price")
    app.run(host='0.0.0.0', port=8080, debug=False)