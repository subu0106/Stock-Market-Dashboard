"""
Utility Helper Functions for Stock Market Dashboard
Contains general utility functions and helpers for the H2O Wave stock application.
"""

from typing import List, Dict, Any, Optional
from ..config.constants import POPULAR_TICKERS


# Cache for ticker suggestions to avoid rebuilding
_suggestion_cache = {}
_sorted_tickers = sorted(POPULAR_TICKERS)  # Pre-sort for faster searching


def get_ticker_suggestions(search_term: str) -> List[str]:
    """Get ticker suggestions based on search term with caching and optimization."""
    if not search_term:
        return POPULAR_TICKERS[:10]  # Return top 10 popular tickers
    
    search_term = search_term.upper()
    suggestions = []
    
    # Use set for O(1) lookup to avoid duplicates
    added = set()
    
    # Exact matches first (most relevant)
    if search_term in _sorted_tickers:
        suggestions.append(search_term)
        added.add(search_term)
    
    # Starts with matches (highly relevant)
    for ticker in _sorted_tickers:
        if len(suggestions) >= 10:
            break
        if ticker.startswith(search_term) and ticker not in added:
            suggestions.append(ticker)
            added.add(ticker)
    
    # Contains matches (less relevant, only if we need more results)
    if len(suggestions) < 10:
        for ticker in _sorted_tickers:
            if len(suggestions) >= 10:
                break
            if search_term in ticker and ticker not in added:
                suggestions.append(ticker)
                added.add(ticker)
    
    return suggestions[:10]


def clear_suggestion_cache() -> None:
    """Clear the ticker suggestion cache (useful for testing or memory management)."""
    global _suggestion_cache
    _suggestion_cache.clear()


def preload_common_searches() -> None:
    """Preload cache for common search patterns to improve initial response time."""
    common_patterns = ['A', 'AA', 'B', 'C', 'D', 'F', 'G', 'M', 'N', 'S', 'T', 'U', 'V', 'W']
    for pattern in common_patterns:
        get_ticker_suggestions(pattern)  # This will cache the results


def format_currency(value: float, precision: int = 2) -> str:
    """Format a number as percentage with proper sign and precision."""
    sign = '+' if value >= 0 else ''
    return f"{sign}{value:.{precision}f}%"


def format_large_number(value: float, unit: str = '') -> str:
    """Format large numbers with appropriate units (K, M, B)."""
    if value == 0 or value is None:
        return "N/A"
    
    if abs(value) >= 1e9:
        return f"{value/1e9:.2f}B{unit}"
    elif abs(value) >= 1e6:
        return f"{value/1e6:.2f}M{unit}"
    elif abs(value) >= 1e3:
        return f"{value/1e3:.2f}K{unit}"
    else:
        return f"{value:.2f}{unit}"


def safe_float_format(value: Any, default: str = "N/A", precision: int = 2) -> str:
    """Safely format a value as float with error handling."""
    try:
        if value is None or value == 0:
            return default
        return f"{float(value):.{precision}f}"
    except (ValueError, TypeError):
        return default


def create_date_range_display(low: float, high: float, currency: bool = True) -> str:
    """Create a formatted date range display string."""
    if low <= 0 or high <= 0:
        return "N/A"
    
    if currency:
        return f"${low:.2f} - ${high:.2f}"
    else:
        return f"{low:.2f} - {high:.2f}"


def validate_ticker_symbol(symbol: str) -> bool:
    """Validate if a ticker symbol is in the correct format."""
    if not symbol:
        return False
    
    # Basic validation: should be uppercase letters, 1-5 characters
    symbol = symbol.upper().strip()
    return symbol.isalpha() and 1 <= len(symbol) <= 5


def sanitize_search_input(search_term: str) -> str:
    """Sanitize and format search input."""
    if not search_term:
        return ""
    
    # Remove extra spaces and convert to uppercase
    return search_term.strip().upper()


def calculate_color_for_change(change_value: float, positive_color: str = '#00ff00', negative_color: str = '#ff4444') -> str:
    """Return appropriate color based on positive/negative change."""
    return positive_color if change_value >= 0 else negative_color


def is_market_hours() -> bool:
    """Check if current time is within market hours (basic implementation)."""
    from datetime import datetime, time
    
    now = datetime.now()
    # Simple check for weekdays between 9:30 AM and 4:00 PM EST
    # This is a basic implementation and doesn't account for holidays
    if now.weekday() >= 5:  # Weekend
        return False
    
    market_open = time(9, 30)  # 9:30 AM
    market_close = time(16, 0)  # 4:00 PM
    current_time = now.time()
    
    return market_open <= current_time <= market_close


def get_trend_indicator(trend_value: float) -> str:
    """Get a visual trend indicator based on the trend value."""
    if trend_value > 5:
        return "📈🔥"  # Strong upward trend
    elif trend_value > 0:
        return "📈"    # Upward trend
    elif trend_value > -5:
        return "📉"    # Downward trend
    else:
        return "📉❄️"  # Strong downward trend


def log_error(error: Exception, context: str = "") -> None:
    """Log errors with context information."""
    error_message = f"Error in {context}: {str(error)}" if context else f"Error: {str(error)}"
    print(error_message)
    # In a production environment, you might want to use proper logging
    # import logging
    # logging.error(error_message, exc_info=True)
