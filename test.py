from app import get_stock_data, get_historical_data, get_ticker_suggestions, POPULAR_TICKERS
import unittest
import random

def get_random_stock():
    """Get a random stock from the stock data"""
    stock_data = get_stock_data()
    if stock_data and len(stock_data) > 0:
        index = random.randrange(len(stock_data))
        return stock_data[index]
    return None

def get_random_ticker():
    """Get a random ticker from popular tickers"""
    index = random.randrange(len(POPULAR_TICKERS))
    return POPULAR_TICKERS[index]

class TestStockApp(unittest.TestCase):
    def setUp(self):
        # Add any common setup code here
        pass
    
    def test_popular_tickers_is_list(self):
        self.assertTrue(type(POPULAR_TICKERS) == list)
        self.assertFalse(type(POPULAR_TICKERS) == tuple)
        self.assertFalse(type(POPULAR_TICKERS) == str)
    
    def test_popular_tickers_not_empty(self):
        self.assertTrue(len(POPULAR_TICKERS) > 0)
        self.assertFalse(len(POPULAR_TICKERS) <= 0)
    
    def test_get_stock_data_returns_list(self):
        stock_data = get_stock_data(['AAPL'])  # Test with single ticker
        self.assertTrue(type(stock_data) == list)
        self.assertFalse(type(stock_data) == tuple)
        self.assertFalse(type(stock_data) == str)
    
    def test_stock_data_element_is_dict(self):
        random_stock = get_random_stock()
        if random_stock:
            self.assertTrue(type(random_stock) == dict)
            self.assertFalse(type(random_stock) == list)
            self.assertFalse(type(random_stock) == tuple)
            self.assertFalse(type(random_stock) == str)
    
    def test_stock_has_required_fields(self):
        random_stock = get_random_stock()
        if random_stock:
            required_fields = ['name', 'symbol', 'price', 'change']
            for field in required_fields:
                self.assertTrue(field in random_stock)
    
    def test_stock_symbol_is_string(self):
        random_stock = get_random_stock()
        if random_stock and 'symbol' in random_stock:
            self.assertTrue(type(random_stock['symbol']) == str)
            self.assertFalse(type(random_stock['symbol']) == int)
            self.assertFalse(type(random_stock['symbol']) == float)
            self.assertFalse(type(random_stock['symbol']) == list)
    
    def test_stock_name_is_string(self):
        random_stock = get_random_stock()
        if random_stock and 'name' in random_stock:
            self.assertTrue(type(random_stock['name']) == str)
            self.assertFalse(type(random_stock['name']) == int)
            self.assertFalse(type(random_stock['name']) == float)
            self.assertFalse(type(random_stock['name']) == list)
    
    def test_stock_price_is_number(self):
        random_stock = get_random_stock()
        if random_stock and 'price' in random_stock:
            self.assertTrue(type(random_stock['price']) in [int, float])
            self.assertFalse(type(random_stock['price']) == str)
            self.assertFalse(type(random_stock['price']) == list)
    
    def test_stock_change_is_number(self):
        random_stock = get_random_stock()
        if random_stock and 'change' in random_stock:
            self.assertTrue(type(random_stock['change']) in [int, float])
            self.assertFalse(type(random_stock['change']) == str)
            self.assertFalse(type(random_stock['change']) == list)
    
    def test_ticker_suggestions_returns_list(self):
        suggestions = get_ticker_suggestions("AA")
        self.assertTrue(type(suggestions) == list)
        self.assertFalse(type(suggestions) == tuple)
        self.assertFalse(type(suggestions) == str)
    
    def test_ticker_suggestions_elements_are_strings(self):
        suggestions = get_ticker_suggestions("A")
        if suggestions and len(suggestions) > 0:
            random_suggestion = suggestions[0]
            self.assertTrue(type(random_suggestion) == str)
            self.assertFalse(type(random_suggestion) == int)
            self.assertFalse(type(random_suggestion) == float)
    
    def test_historical_data_structure(self):
        random_ticker = get_random_ticker()
        hist_data = get_historical_data(random_ticker)
        if hist_data:
            self.assertTrue(type(hist_data) == dict)
            self.assertTrue('chart_data' in hist_data)
            self.assertTrue('current_price' in hist_data)
            self.assertTrue(type(hist_data['chart_data']) == list)
    
    def test_empty_stock_data_handling(self):
        stock_data = get_stock_data([])  # Empty list
        self.assertTrue(type(stock_data) == list)
        # Should return empty list for empty input
    
    def test_invalid_ticker_handling(self):
        stock_data = get_stock_data(['INVALID_TICKER_12345'])
        self.assertTrue(type(stock_data) == list)
        # Should handle invalid tickers gracefully

if __name__ == '__main__':
    unittest.main()  
    