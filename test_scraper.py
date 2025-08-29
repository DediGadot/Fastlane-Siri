#!/usr/bin/env python3
"""
Test the scraper module
"""
import sys
from scraper import extract_price, validate_price

def test_extract_price():
    """Test price extraction with sample HTML"""
    
    # Test case 1: Hebrew format
    html1 = """
    <html>
    <body>
    <p>המחיר עכשיו 8 ₪</p>
    </body>
    </html>
    """
    
    price1 = extract_price(html1)
    assert price1 == 8, f"Expected 8, got {price1}"
    print("✅ Hebrew format test passed")
    
    # Test case 2: Symbol first
    html2 = """
    <html>
    <body>
    <div>Current price: ₪8</div>
    </body>
    </html>
    """
    
    price2 = extract_price(html2)
    assert price2 == 8, f"Expected 8, got {price2}"
    print("✅ Symbol first test passed")
    
    # Test case 3: No price
    html3 = """
    <html>
    <body>
    <p>No pricing information here</p>
    </body>
    </html>
    """
    
    price3 = extract_price(html3)
    assert price3 is None, f"Expected None, got {price3}"
    print("✅ No price test passed")
    
    # Test case 4: Invalid price (too high)
    html4 = """
    <html>
    <body>
    <p>המחיר עכשיו 999 ₪</p>
    </body>
    </html>
    """
    
    price4 = extract_price(html4)
    assert price4 is None, f"Expected None for invalid price, got {price4}"
    print("✅ Invalid price test passed")

def test_validate_price():
    """Test price validation"""
    assert validate_price(8) == True
    assert validate_price(1) == True
    assert validate_price(100) == True
    assert validate_price(0) == False
    assert validate_price(101) == False
    assert validate_price(None) == False
    assert validate_price("8") == False
    print("✅ Price validation tests passed")

def test_real_website():
    """Test against real website (if available)"""
    try:
        import requests
        print("🌐 Testing against real website...")
        
        response = requests.get('https://fastlane.co.il/', timeout=10)
        price = extract_price(response.text)
        
        if price:
            print(f"✅ Real website test passed: {price} NIS")
            assert validate_price(price), f"Invalid price from real site: {price}"
        else:
            print("⚠️  Could not extract price from real website (might be down)")
            
    except Exception as e:
        print(f"⚠️  Real website test failed: {e}")

if __name__ == "__main__":
    print("🧪 Testing Fast Lane Price Scraper")
    print("=" * 40)
    
    try:
        test_extract_price()
        test_validate_price() 
        test_real_website()
        
        print("\n🎉 All tests passed!")
        sys.exit(0)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)