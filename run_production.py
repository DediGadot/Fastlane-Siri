#!/usr/bin/env python3
"""
Production runner for Fast Lane service
Uses Waitress WSGI server instead of Flask dev server
"""
import logging
from waitress import serve
from app import app, init_db

if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize database
    init_db()
    
    print("=" * 50)
    print("🛣️  Fast Lane Price Service - Production Mode")
    print("=" * 50)
    print("Port: 8080")
    print("Threads: 4")
    print("Cache TTL: 5 minutes")
    print("")
    print("Endpoints:")
    print("  GET /price  - Current toll price") 
    print("  GET /health - Health check")
    print("  GET /stats  - Request statistics")
    print("")
    print("For Siri: http://YOUR-SERVER-IP:8080/price")
    print("=" * 50)
    
    # Start production server
    try:
        serve(
            app, 
            host='0.0.0.0', 
            port=8080, 
            threads=4,
            cleanup_interval=30,
            channel_timeout=120
        )
    except KeyboardInterrupt:
        print("\n👋 Service stopped")
    except Exception as e:
        print(f"💥 Server error: {e}")
        exit(1)