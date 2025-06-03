#!/usr/bin/env python3
"""
Comprehensive tests for Stock Market Dashboard
Tests all functionality of the application components.
"""

import sys
import os

print("🧪 Running Comprehensive Stock Market Dashboard Tests")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

# Add the project root directory to the path so we can import the src package
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..')
print(f"Adding to path: {project_root}")
sys.path.insert(0, project_root)

def test_imports():
    """Test that all main modules can be imported successfully."""
    print("\n📋 Testing imports...")
    
    tests = [
        ("StockService", "from src.data.stock_service import StockService"),
        ("Components", "from src.ui.components import create_header_card"),
        ("Helpers", "from src.utils.helpers import get_ticker_suggestions"),
        ("Constants", "from src.config.constants import POPULAR_TICKERS"),
    ]
    
    passed = 0
    for name, import_statement in tests:
        try:
            exec(import_statement)
            print(f"✅ {name} import successful")
            passed += 1
        except Exception as e:
            print(f"❌ {name} import failed: {e}")
    
    return passed == len(tests)

def test_constants():
    """Test configuration constants."""
    print("\n📋 Testing constants...")
    
    try:
        from src.config.constants import POPULAR_TICKERS, THEMES, CHART_PERIOD_MAPPING
        
        # Test popular tickers
        assert isinstance(POPULAR_TICKERS, list)
        assert len(POPULAR_TICKERS) > 0
        assert "AAPL" in POPULAR_TICKERS
        print(f"✅ Popular tickers loaded ({len(POPULAR_TICKERS)} tickers)")
        
        # Test themes
        assert isinstance(THEMES, dict)
        assert "h2o-dark" in THEMES
        assert "h2o-light" in THEMES
        print("✅ Themes configuration loaded")
        
        # Test chart period mapping
        assert isinstance(CHART_PERIOD_MAPPING, dict)
        assert "1M" in CHART_PERIOD_MAPPING
        print("✅ Chart period mapping loaded")
        
        return True
    except Exception as e:
        print(f"❌ Constants test failed: {e}")
        return False

def test_stock_service():
    """Test basic StockService functionality."""
    print("\n📋 Testing StockService...")
    
    try:
        from src.data.stock_service import StockService
        
        # Initialize service
        service = StockService()
        print("✅ StockService initialized")
        
        # Test cache functionality
        cache_stats = service.get_cache_stats()
        assert 'stock_data_cache_size' in cache_stats
        assert 'chart_data_cache_size' in cache_stats
        print("✅ Cache stats working")
        
        # Test that service has expected methods
        assert hasattr(service, 'get_stock_data')
        assert hasattr(service, 'get_chart_data')
        print("✅ Service methods available")
        
        return True
    except Exception as e:
        print(f"❌ StockService test failed: {e}")
        return False

def test_helpers():
    """Test utility helper functions."""
    print("\n📋 Testing helpers...")
    
    try:
        from src.utils.helpers import (
            get_ticker_suggestions, 
            format_currency, 
            validate_ticker_symbol,
            sanitize_search_input
        )
        
        # Test ticker suggestions
        suggestions = get_ticker_suggestions("A")
        assert isinstance(suggestions, list)
        print("✅ Ticker suggestions working")
        
        # Test currency formatting
        formatted = format_currency(5.67)
        assert "+5.67%" in formatted
        print("✅ Currency formatting working")
        
        # Test ticker validation
        assert validate_ticker_symbol("AAPL") == True
        assert validate_ticker_symbol("") == False
        print("✅ Ticker validation working")
        
        # Test search input sanitization
        clean_input = sanitize_search_input("  aapl  ")
        assert clean_input == "AAPL"
        print("✅ Search sanitization working")
        
        return True
    except Exception as e:
        print(f"❌ Helpers test failed: {e}")
        return False

def test_ui_components():
    """Test UI component creation."""
    print("\n📋 Testing UI components...")
    
    try:
        from src.ui.components import create_header_card, create_search_section
        
        # Test header card creation
        header = create_header_card()
        assert header is not None
        print("✅ Header card creation working")
        
        # Test search section creation  
        search_components = create_search_section()
        assert isinstance(search_components, list)
        assert len(search_components) > 0
        print("✅ Search section creation working")
        
        return True
    except Exception as e:
        print(f"❌ UI components test failed: {e}")
        return False

def main():
    """Run all tests and report results."""
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Constants Test", test_constants),
        ("StockService Test", test_stock_service),
        ("Helpers Test", test_helpers),
        ("UI Components Test", test_ui_components),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
