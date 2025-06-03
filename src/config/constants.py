"""
Configuration constants for the Stock Market Dashboard.
"""

POPULAR_TICKERS = [
    'AAPL', 'GOOGL', 'GOOG', 'AMZN', 'MSFT', 'NVDA', 'META', 'NFLX', 'ADBE', 'CRM',
    'ORCL', 'IBM', 'INTC', 'AMD', 'QCOM', 'AVGO', 'CSCO', 'PYPL', 'SQ', 'UBER',
    'LYFT', 'SNAP', 'TWTR', 'ZOOM', 'TSLA', 'F', 'GM', 'NIO', 'NVDA'
]

CHART_PERIOD_MAPPING = {
    '5D': '5d', 
    '1M': '1mo',
    '6M': '6mo',
    '1Y': '1y',
    '5Y': '5y',
    'Max': 'max'
}

THEMES = {
    'h2o-light': {
        'bg_color': '#ffffff',
        'secondary_bg': '#f5f5f5',
        'accent_color': '#1f4e79',
        'text_color': '#333333',
        'border_color': '#1f4e79',
        'button_text_color': '#000',
        'button_hover_color': '#2c5f99',
        'row_hover_color': '#e6e6e6'
    },
    'h2o-dark': {
        'bg_color': '#1a1a1a',
        'secondary_bg': '#2d2d2d',
        'accent_color': '#f1c232',
        'text_color': '#ffffff',
        'border_color': '#f1c232',
        'button_text_color': '#000',
        'button_hover_color': '#ffd966',
        'row_hover_color': '#333333'
    }
}

DEFAULT_SETTINGS = {
    'default_theme': 'h2o-dark',
    'default_chart_period': '1M',
    'refresh_interval': 30,
    'max_suggestions': 10,
    'top_gainers_count': 5
}

APP_CONFIG = {
    'title': '📈 Stock Market Dashboard',
    'subtitle': 'H2O WAVE STOCK APPLICATION',
    'icon': 'TrendingUp',
    'footer_text': '''Subavarshana Arumugam\n©2025 All rights reserved.'''
}
