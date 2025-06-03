"""
Main Application Logic for Stock Market Dashboard
Central application logic and route handling for the H2O Wave stock application.
"""

from h2o_wave import Q, app, ui
import asyncio
from typing import List, Dict, Any

from .config.constants import POPULAR_TICKERS, DEFAULT_SETTINGS
from .data.stock_service import StockService
from .ui.components import (
    create_header_card, create_search_section, create_stock_details_section,
    create_chart_period_buttons, create_price_chart, create_stocks_table,
    create_no_data_message, create_footer_card
)
from .ui.theme import handle_toggle_theme, initialize_theme, get_current_theme
from .utils.helpers import get_ticker_suggestions, log_error, preload_common_searches


class StockMarketApp:
    """Main application class for the Stock Market Dashboard."""
    
    def __init__(self):
        """Initialize the application with required services."""
        self.stock_service = StockService()
        # Preload common search patterns for faster initial responses
        preload_common_searches()
    
    async def initialize_client(self, q: Q) -> None:
        """Initialize a new client session with default settings."""
        try:
            initialize_theme(q)
            q.client.search_symbols = POPULAR_TICKERS.copy()
            q.client.chart_period = DEFAULT_SETTINGS['default_chart_period']
            q.client.theme = DEFAULT_SETTINGS['default_theme']
            q.client.initialized = True
        except Exception as e:
            log_error(e, "initialize_client")
    
    async def handle_theme_toggle(self, q: Q) -> None:
        """Handle theme toggle request."""
        try:
            await handle_toggle_theme(q)
        except Exception as e:
            log_error(e, "handle_theme_toggle")
    
    async def handle_chart_period_change(self, q: Q) -> None:
        """Handle chart period selection change with optimized UI update."""
        try:
            if q.args.chart_period:
                new_period = q.args.chart_period
                q.client.chart_period = new_period
                
                # If we're viewing a single stock, provide instant feedback
                if hasattr(q.client, 'search_symbols') and len(q.client.search_symbols) == 1:
                    symbol = q.client.search_symbols[0]
                    if symbol not in POPULAR_TICKERS:
                        await self._update_chart_only(q, symbol, new_period)
                        return  # Skip full page render for faster response
        except Exception as e:
            log_error(e, "handle_chart_period_change")
    
    async def handle_search_input(self, q: Q) -> None:
        """Handle stock ticker search input with optimization."""
        try:
            if q.args.search_ticker:
                search_term = q.args.search_ticker.strip()
                if search_term:
                    # Check cache first for instant response
                    cached_results = self.stock_service.get_cached_search_results(search_term)
                    
                    search_symbols = [search_term.upper()]
                    q.client.search_symbols = search_symbols
                else:
                    q.client.search_symbols = POPULAR_TICKERS.copy()
            elif q.args.reset_search:
                q.client.search_symbols = POPULAR_TICKERS.copy()
        except Exception as e:
            log_error(e, "handle_search_input")
    
    async def get_fast_suggestions(self, search_term: str) -> List[str]:
        """Get ticker suggestions with caching for faster response."""
        try:
            # Check cache first
            cached_results = self.stock_service.get_cached_search_results(search_term)
            if cached_results is not None:
                return cached_results
            
            # Generate new suggestions
            suggestions = get_ticker_suggestions(search_term)
            
            # Cache the results
            self.stock_service.cache_search_results(search_term, suggestions)
            
            return suggestions
        except Exception as e:
            log_error(e, "get_fast_suggestions")
            return []
    
    async def create_content_items(self, q: Q) -> List[ui.Component]:
        """Create main content items for the dashboard."""
        content_items = []
        
        try:
            current_search = q.args.search_ticker if q.args.search_ticker else ""
            suggestions = await self.get_fast_suggestions(current_search)
            
            content_items.extend(create_search_section(current_search, suggestions))
            
            search_stock_data = self.stock_service.get_stock_data(q.client.search_symbols)
            default_stock_data = self.stock_service.get_stock_data(POPULAR_TICKERS)
            
            if search_stock_data:
                is_single_stock = len(q.client.search_symbols) == 1 and q.client.search_symbols != POPULAR_TICKERS
                
                if is_single_stock:
                    await self._create_single_stock_content(q, search_stock_data[0], content_items)
                
                table_data = default_stock_data[:5]
                content_items.extend([ui.separator()])
                content_items.extend(create_stocks_table(table_data, '🏆 Top Gainers'))
                
            else:
                if default_stock_data:
                    content_items.extend(create_no_data_message())
                    content_items.extend(create_stocks_table(default_stock_data[:5], '🏆 Top Gainers'))
            
        except Exception as e:
            log_error(e, "create_content_items")
            content_items.append(ui.text("**Error loading dashboard content. Please try again.**"))
        
        return content_items
    
    async def _create_single_stock_content(self, q: Q, stock: Dict[str, Any], content_items: List[ui.Component]) -> None:
        """Create detailed content for a single stock."""
        try:
            symbol = stock['symbol']
            trend_data = self.stock_service.get_historical_data(symbol)
            current_period = q.client.chart_period if hasattr(q.client, 'chart_period') else '1M'
            
            # Check if chart data is cached
            cache_key = f"{symbol}_{current_period}"
            is_cached = self.stock_service._is_chart_cache_valid(cache_key)
            
            # Get chart data with caching support
            chart_data = self.stock_service.get_chart_data(symbol, current_period)
            
            # Preload other chart periods in the background for instant switching
            if not hasattr(q.client, f'preloaded_{symbol}'):
                # Mark as preloaded to avoid repeated preloading
                setattr(q.client, f'preloaded_{symbol}', True)
                # Start background preloading immediately
                asyncio.create_task(self.stock_service.async_preload_chart_data(symbol))
                # Also trigger immediate preloading for most common periods
                asyncio.create_task(self._immediate_preload_common_periods(symbol))
            
            content_items.extend(create_stock_details_section(stock, trend_data))
            content_items.extend(create_chart_period_buttons(current_period))
            content_items.extend(create_price_chart(symbol, chart_data, current_period, is_cached))
            
        except Exception as e:
            log_error(e, f"_create_single_stock_content for {stock.get('symbol', 'unknown')}")
            content_items.append(ui.text(f"**Error loading detailed data for {stock.get('symbol', 'stock')}**"))
    
    async def _update_chart_only(self, q: Q, symbol: str, period: str) -> None:
        """Update only the chart component for faster period switching."""
        try:
            # Check cache status
            cache_key = f"{symbol}_{period}"
            is_cached = self.stock_service._is_chart_cache_valid(cache_key)
            
            # Get chart data (should be instant if cached from preloading)
            chart_data = self.stock_service.get_chart_data(symbol, period)
            
            # Use streamlined full page render since it's still fast with cached data
            # This ensures all components remain synchronized
            await self.render_page(q)
            
        except Exception as e:
            log_error(e, f"_update_chart_only for {symbol}")
            # Fallback to full page render if chart-only update fails
            await self.render_page(q)

    async def _immediate_preload_common_periods(self, symbol: str) -> None:
        """Immediately preload the most commonly used chart periods."""
        try:
            # Preload the most common periods first for fastest switching
            priority_periods = ['1M', '6M', '1Y']  # Most commonly used periods
            
            for period in priority_periods:
                cache_key = f"{symbol}_{period}"
                if not self.stock_service._is_chart_cache_valid(cache_key):
                    # Use get_chart_data to fetch and cache immediately
                    await asyncio.get_event_loop().run_in_executor(
                        None, self.stock_service.get_chart_data, symbol, period
                    )
                    
        except Exception as e:
            log_error(e, f"_immediate_preload_common_periods for {symbol}")

    async def render_page(self, q: Q) -> None:
        """Render the complete dashboard page."""
        try:
            current_theme = get_current_theme(q)
            q.page['header'] = create_header_card(current_theme)
            content_items = await self.create_content_items(q)
            q.page['content'] = ui.form_card(box='content', items=content_items)
            q.page['footer'] = create_footer_card()
            await q.page.save()
            
        except Exception as e:
            log_error(e, "render_page")
            # Fallback error page
            q.page['content'] = ui.form_card(
                box='content',
                items=[ui.text("**Application Error**: Unable to load dashboard. Please refresh the page.")]
            )
            await q.page.save()


# Global app instance
stock_app = StockMarketApp()


@app('/')
async def serve(q: Q):
    """Main application route handler."""
    try:
        if not getattr(q.client, 'initialized', False):
            await stock_app.initialize_client(q)
        
        if q.args.toggle_theme:
            await stock_app.handle_theme_toggle(q)
            return
        
        if q.args.chart_period:
            await stock_app.handle_chart_period_change(q)
        
        if q.args.search_ticker or q.args.reset_search:
            await stock_app.handle_search_input(q)
        
        await stock_app.render_page(q)
        
    except Exception as e:
        log_error(e, "main serve function")
        q.page['content'] = ui.form_card(
            box='content',
            items=[ui.text("**Critical Error**: Application encountered an unexpected error. Please refresh the page.")]
        )
        await q.page.save()
