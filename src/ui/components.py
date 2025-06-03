"""
UI Components for Stock Market Dashboard
Contains reusable UI component functions for the H2O Wave stock application.
"""

from h2o_wave import ui, data
from typing import List, Dict, Any, Optional
from ..config.constants import THEMES, CHART_PERIOD_MAPPING


def create_header_card(current_theme: str = 'h2o-dark') -> ui.HeaderCard:
    """Create the main header card with theme toggle button."""
    theme_icon = '🌞' if current_theme == 'h2o-dark' else '🌙'
    
    return ui.header_card(
        box='header',
        subtitle="H2O WAVE STOCK APPLICATION",
        icon='TrendingUp',
        title='📊 Stock Market Dashboard',
        items=[
            ui.button(
                name='toggle_theme',
                label=f'{theme_icon}',
                tooltip='Switch theme',
                primary=False
            )
        ]
    )


def create_search_section(current_search: str = "", suggestions: List[str] = None, loading: bool = False) -> List[ui.Component]:
    """Create the stock search section components with loading state."""
    if suggestions is None:
        suggestions = []
    
    search_items = [
        ui.combobox(
            name='search_ticker',
            label='🔍 Search Stock by Ticker Symbol' + (' (Loading...)' if loading else ''),
            placeholder='Enter ticker symbol (e.g., AAPL, GOOGL, TSLA)',
            value=current_search,
            choices=[ticker for ticker in suggestions],
            trigger=True,
            disabled=loading
        ),
        ui.button(name='reset_search', label='Show Stocks Info', primary=False, disabled=loading),
    ]
    
    if loading:
        search_items.append(ui.progress(label="Searching...", caption="Finding matching tickers"))
    
    search_items.append(ui.separator())
    return search_items


def create_stock_details_section(stock: Dict[str, Any], trend_data: Optional[Dict[str, Any]] = None) -> List[ui.Component]:
    """Create detailed stock information section for a single stock."""
    components = []
    
    day_range = f"${stock['day_low']:.2f} - ${stock['day_high']:.2f}" if stock['day_low'] > 0 and stock['day_high'] > 0 else "N/A"
    year_range = f"${stock['fifty_two_week_low']:.2f} - ${stock['fifty_two_week_high']:.2f}" if stock['fifty_two_week_low'] > 0 and stock['fifty_two_week_high'] > 0 else "N/A"
    market_cap_formatted = f"${stock['market_cap']/1e9:.2f}B" if stock['market_cap'] > 0 else "N/A"
    volume_formatted = f"{stock['volume']/1e6:.2f}M" if stock['volume'] > 0 else "N/A"
    pe_ratio_formatted = f"{stock['pe_ratio']:.2f}" if stock['pe_ratio'] > 0 else 'N/A'
    
    components.extend([
        ui.text(f"**📈 {stock['symbol']} - {stock['name']}**"),
        ui.text(f"**Price:** ${stock['price']:.2f} | **Change:** {'+' if stock['change'] >= 0 else ''}{stock['change']:.2f}%"),
        ui.text(f"**Day Range:** {day_range} | **52-Week:** {year_range}"),
        ui.text(f"**Market Cap:** {market_cap_formatted} | **Volume:** {volume_formatted} | **P/E:** {pe_ratio_formatted}")
    ])
    
    if trend_data:
        trend_info = f"1M Trend: {'+' if trend_data['trend_change'] >= 0 else ''}{trend_data['trend_change']:.2f}% | Vol Trend: {'+' if trend_data['volume_trend'] >= 0 else ''}{trend_data['volume_trend']:.1f}%"
        components.append(ui.text(f"**{trend_info}**"))
    
    components.append(ui.separator())
    
    return components


def create_chart_period_buttons(current_period: str = '1M', loading_period: str = None) -> List[ui.Component]:
    """Create chart period selection buttons with loading state."""
    buttons = []
    periods = ['5D', '1M', '6M', '1Y', '5Y', 'Max']
    
    for period in periods:
        is_current = (current_period == period)
        is_loading = (loading_period == period)
        
        button_label = period
        if is_loading:
            button_label = f"{period} ⏳"
        
        buttons.append(
            ui.button(
                name='chart_period', 
                value=period, 
                label=button_label, 
                primary=is_current,
                disabled=is_loading
            )
        )
    
    return [
        ui.text('**📈 Chart Time Period**'),
        ui.buttons(buttons)
    ]


def create_price_chart(symbol: str, chart_data: List[List], period: str = '1M', cached: bool = False) -> List[ui.Component]:
    """Create price chart visualization with cache indicator."""
    cache_indicator = " 🚀" if cached else " ⏳"
    
    if chart_data and len(chart_data) > 0:
        return [
            ui.text(f'**📊 {symbol} Price Chart ({period}){cache_indicator}**'),
            ui.visualization(
                data=data(fields=['date', 'price'], rows=chart_data, pack=True),
                plot=ui.plot([
                    ui.mark(
                        type='line',
                        x='=date',
                        y='=price',
                        color='#f1c232'
                    )
                ]),
                height='300px'
            )
        ]
    else:
        return [ui.text(f'**📊 {symbol} Price Chart ({period})** - Chart data unavailable')]


def create_stocks_table(stock_data: List[Dict[str, Any]], title: str = '🏆 Top Gainers') -> List[ui.Component]:
    """Create stocks data table."""
    # Create table rows
    table_rows = []
    for stock in stock_data:
        table_rows.append(
            ui.table_row(
                name=stock['symbol'],
                cells=[
                    stock['symbol'],
                    stock['name'],
                    f"${stock['price']:.2f}",
                    f"{'+' if stock['change'] >= 0 else ''}{stock['change']:.2f}%",
                ]
            )
        )
    
    return [
        ui.text(f'**{title}**'),
        ui.table(
            name='stocks_table',
            columns=[
                ui.table_column(name='symbol', label='Symbol', sortable=True),
                ui.table_column(name='name', label='Company'),
                ui.table_column(name='price', label='Price ($)', data_type='number', sortable=True),
                ui.table_column(name='change', label='% Change', data_type='number', sortable=True),
            ],
            rows=table_rows,
            height='300px'
        )
    ]


def create_no_data_message() -> List[ui.Component]:
    """Create message when search results are not found."""
    return [
        ui.text('**Search Result Not Found**'),
        ui.text('Unable to fetch data for the searched ticker symbol. Please try a different symbol or check your internet connection.'),
        ui.separator()
    ]


def create_footer_card() -> ui.FooterCard:
    """Create the main footer card."""
    return ui.footer_card(
        box='footer',
        caption='''
        Subavarshana Arumugam
        ©2025 All rights reserved.'''
    )
