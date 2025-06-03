"""
Stock data service for fetching and processing market data.
"""

import yfinance as yf
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from ..config.constants import POPULAR_TICKERS, CHART_PERIOD_MAPPING
from ..utils.helpers import get_ticker_suggestions


class StockService:
    """Service class for handling stock data operations with caching."""
    
    def __init__(self):
        """Initialize the service with cache storage."""
        self._stock_data_cache = {}
        self._cache_timestamps = {}
        self._cache_duration = 300  # 5 minutes cache
        
        # Chart data caching - separate cache for better performance
        self._chart_data_cache = {}
        self._chart_cache_timestamps = {}
        self._chart_cache_duration = 600  # 10 minutes cache for chart data
        
        # Search caching
        self._search_cache = {}
        self._search_cache_duration = 1800  # 30 minutes for search results
        
        # Debounce tasks
        self._debounce_tasks = {}
    
    def _is_cache_valid(self, symbol: str) -> bool:
        """Check if cached data is still valid."""
        if symbol not in self._cache_timestamps:
            return False
        
        cache_time = self._cache_timestamps[symbol]
        return datetime.now() - cache_time < timedelta(seconds=self._cache_duration)
    
    def _is_chart_cache_valid(self, cache_key: str) -> bool:
        """Check if cached chart data is still valid."""
        if cache_key not in self._chart_cache_timestamps:
            return False
        
        cache_time = self._chart_cache_timestamps[cache_key]
        return datetime.now() - cache_time < timedelta(seconds=self._chart_cache_duration)
    
    def _get_chart_from_cache(self, cache_key: str) -> Optional[List[List]]:
        """Get chart data from cache if valid."""
        if self._is_chart_cache_valid(cache_key):
            return self._chart_data_cache.get(cache_key)
        return None
    
    def _store_chart_in_cache(self, cache_key: str, data: List[List]) -> None:
        """Store chart data in cache."""
        self._chart_data_cache[cache_key] = data
        self._chart_cache_timestamps[cache_key] = datetime.now()
    
    def _get_from_cache(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get stock data from cache if valid."""
        if self._is_cache_valid(symbol):
            return self._stock_data_cache.get(symbol)
        return None
    
    def _store_in_cache(self, symbol: str, data: Dict[str, Any]) -> None:
        """Store stock data in cache."""
        self._stock_data_cache[symbol] = data
        self._cache_timestamps[symbol] = datetime.now()
    
    def get_stock_data(self, symbols: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Get stock data for given symbols with caching support.
        
        Args:
            symbols: List of stock symbols. If None, uses POPULAR_TICKERS.
            
        Returns:
            List of dictionaries containing stock data.
        """
        if symbols is None:
            symbols = POPULAR_TICKERS
        
        if not symbols:
            return []
        
        try:
            data_list = []
            symbols_to_fetch = []
            
            # Check cache first
            for symbol in symbols:
                cached_data = self._get_from_cache(symbol)
                if cached_data:
                    data_list.append(cached_data)
                else:
                    symbols_to_fetch.append(symbol)
            
            # Fetch only non-cached symbols
            if symbols_to_fetch:
                tickers = yf.Tickers(" ".join(symbols_to_fetch))

                for symbol in symbols_to_fetch:
                    try:
                        t = tickers.tickers[symbol].info
                        price = t.get('regularMarketPrice', 0)
                        change = t.get('regularMarketChangePercent', 0)
                        
                        volume = t.get('regularMarketVolume', 0)
                        market_cap = t.get('marketCap', 0)
                        pe_ratio = t.get('trailingPE', 0)
                        day_high = t.get('regularMarketDayHigh', 0)
                        day_low = t.get('regularMarketDayLow', 0)
                        fifty_two_week_high = t.get('fiftyTwoWeekHigh', 0)
                        fifty_two_week_low = t.get('fiftyTwoWeekLow', 0)
                        
                        stock_data = {
                            'name': t.get('shortName', symbol),
                            'symbol': symbol,
                            'price': price,
                            'change': change,
                            'volume': volume,
                            'market_cap': market_cap,
                            'pe_ratio': pe_ratio,
                            'day_high': day_high,
                            'day_low': day_low,
                            'fifty_two_week_high': fifty_two_week_high,
                            'fifty_two_week_low': fifty_two_week_low
                        }
                        
                        data_list.append(stock_data)
                        self._store_in_cache(symbol, stock_data)
                        
                    except Exception as e:
                        print(f"Error fetching data for {symbol}: {e}")
                        continue
            
            return sorted(data_list, key=lambda x: x['change'], reverse=True)
        except Exception as e:
            print(f"Error fetching stock data: {e}")
            return []

    @staticmethod
    def get_historical_data(symbol: str, period: str = "1mo") -> Optional[Dict[str, Any]]:
        """
        Get historical data for trend analysis and chart display.
        
        Args:
            symbol: Stock symbol to fetch data for.
            period: Time period for historical data.
            
        Returns:
            Dictionary containing historical data and trend analysis.
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            if not hist.empty:
                # Calculate trend indicators
                current_price = hist['Close'].iloc[-1]
                start_price = hist['Close'].iloc[0]
                trend_change = ((current_price - start_price) / start_price) * 100
                
                # Get recent volume trend
                avg_volume = hist['Volume'].mean()
                recent_volume = hist['Volume'].iloc[-1]
                volume_trend = ((recent_volume - avg_volume) / avg_volume) * 100
                
                # Format data for charting
                chart_data = []
                for date, row in hist.iterrows():
                    chart_data.append([
                        date.strftime('%Y-%m-%d'),  # x-axis (date)
                        float(row['Close'])         # y-axis (closing price)
                    ])
                
                return {
                    'trend_change': trend_change,
                    'volume_trend': volume_trend,
                    'high_period': hist['High'].max(),
                    'low_period': hist['Low'].min(),
                    'avg_volume': avg_volume,
                    'chart_data': chart_data,
                    'current_price': current_price,
                    'start_price': start_price
                }
        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {e}")
        
        return None

    def get_chart_data(self, symbol: str, period: str = "1mo") -> List[List]:
        """
        Get formatted chart data for different time periods with caching.
        
        Args:
            symbol: Stock symbol to fetch data for.
            period: Chart time period (1D, 5D, 1M, etc.).
            
        Returns:
            List of [date, price] pairs for charting.
        """
        # Create cache key combining symbol and period
        cache_key = f"{symbol}_{period}"
        
        # Check cache first for instant response
        cached_data = self._get_chart_from_cache(cache_key)
        if cached_data is not None:
            return cached_data
        
        yf_period = CHART_PERIOD_MAPPING.get(period, '1mo')
        
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=yf_period)
            
            if hist.empty:
                return []
                
            # Format data as simple list of [date, price] pairs
            chart_data = []
            for date, row in hist.iterrows():
                chart_data.append([
                    date.strftime('%Y-%m-%d'),
                    round(float(row['Close']), 2)
                ])
            
            # Cache the result
            self._store_chart_in_cache(cache_key, chart_data)
            return chart_data
        except Exception as e:
            print(f"Error fetching chart data for {symbol}: {e}")
            return []

    @staticmethod
    def get_ticker_suggestions(search_term: str) -> List[str]:
        """
        Get ticker suggestions based on search term using optimized helper.
        
        Args:
            search_term: Search string to match against tickers.
            
        Returns:
            List of matching ticker symbols.
        """
        return get_ticker_suggestions(search_term)
    
    async def debounced_search(self, search_term: str, delay: float = 0.3) -> List[str]:
        """
        Perform debounced search to reduce API calls during typing.
        
        Args:
            search_term: Search string to match against tickers.
            delay: Delay in seconds before executing search.
            
        Returns:
            List of matching ticker symbols.
        """
        # Cancel previous search task if it exists
        if search_term in self._debounce_tasks:
            self._debounce_tasks[search_term].cancel()
        
        # Create new debounced task
        async def delayed_search():
            await asyncio.sleep(delay)
            return self.get_ticker_suggestions(search_term)
        
        task = asyncio.create_task(delayed_search())
        self._debounce_tasks[search_term] = task
        
        try:
            result = await task
            # Clean up completed task
            if search_term in self._debounce_tasks:
                del self._debounce_tasks[search_term]
            return result
        except asyncio.CancelledError:
            return []
    
    def get_cached_search_results(self, search_term: str) -> Optional[List[str]]:
        """
        Get cached search results if available and valid.
        
        Args:
            search_term: Search string.
            
        Returns:
            Cached search results or None if not available/expired.
        """
        cache_key = search_term.upper()
        if cache_key in self._search_cache:
            cached_data, timestamp = self._search_cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=self._search_cache_duration):
                return cached_data
        return None
    
    def cache_search_results(self, search_term: str, results: List[str]) -> None:
        """
        Cache search results for faster subsequent searches.
        
        Args:
            search_term: Search string.
            results: Search results to cache.
        """
        cache_key = search_term.upper()
        self._search_cache[cache_key] = (results, datetime.now())
        
        # Limit cache size to prevent memory issues
        if len(self._search_cache) > 100:
            # Remove oldest entries
            oldest_key = min(self._search_cache.keys(), 
                           key=lambda k: self._search_cache[k][1])
            del self._search_cache[oldest_key]
    
    def preload_chart_data(self, symbol: str) -> None:
        """
        Preload chart data for all common periods to eliminate loading delays.
        
        Args:
            symbol: Stock symbol to preload data for.
        """
        # Prioritize most commonly used periods first
        priority_periods = ['1M', '6M', '1Y']  # Load these first for fastest switching
        secondary_periods = ['5D', '5Y', 'Max']  # Load these after
        
        all_periods = priority_periods + secondary_periods
        
        for period in all_periods:
            cache_key = f"{symbol}_{period}"
            # Only fetch if not already cached
            if not self._is_chart_cache_valid(cache_key):
                try:
                    self.get_chart_data(symbol, period)
                except Exception as e:
                    print(f"Error preloading chart data for {symbol} ({period}): {e}")
    
    async def async_preload_chart_data(self, symbol: str) -> None:
        """
        Asynchronously preload chart data to avoid blocking the UI.
        
        Args:
            symbol: Stock symbol to preload data for.
        """
        await asyncio.get_event_loop().run_in_executor(None, self.preload_chart_data, symbol)
    
    def clear_chart_cache(self) -> None:
        """Clear all chart data cache."""
        self._chart_data_cache.clear()
        self._chart_cache_timestamps.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        return {
            'stock_data_cache_size': len(self._stock_data_cache),
            'chart_data_cache_size': len(self._chart_data_cache),
            'search_cache_size': len(self._search_cache),
            'active_debounce_tasks': len(self._debounce_tasks),
            'chart_cache_hit_rate': self._calculate_chart_hit_rate(),
            'cached_periods': list(set([k.split('_')[1] for k in self._chart_data_cache.keys()])),
            'cached_symbols': list(set([k.split('_')[0] for k in self._chart_data_cache.keys()]))
        }
    
    def _calculate_chart_hit_rate(self) -> float:
        """Calculate chart cache hit rate."""
        valid_entries = sum(1 for key in self._chart_data_cache.keys() 
                          if self._is_chart_cache_valid(key))
        total_entries = len(self._chart_data_cache)
        return valid_entries / total_entries if total_entries > 0 else 0.0
