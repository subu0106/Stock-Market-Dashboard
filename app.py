from h2o_wave import Q, app, main, ui, data
import yfinance as yf

POPULAR_TICKERS = [
   
    'AAPL', 'GOOGL', 'GOOG', 'AMZN', 'MSFT', 'NVDA', 'META', 'NFLX', 'ADBE', 'CRM',
    'ORCL', 'IBM', 'INTC', 'AMD', 'QCOM', 'AVGO', 'CSCO', 'PYPL', 'SQ', 'UBER',
    'LYFT', 'SNAP', 'TWTR', 'ZOOM', 'TSLA', 'F', 'GM', 'NIO', 'NVDA'
]

def get_stock_data(symbols=None):
    """Get stock data for given symbols or default POPULAR_TICKERS list"""
    if symbols is None:
        symbols = POPULAR_TICKERS
    
    if not symbols:
        return []
    
    try:
        tickers = yf.Tickers(" ".join(symbols))
        data_list = []

        for symbol in symbols:
            try:
                t = tickers.tickers[symbol].info
                price = t.get('regularMarketPrice', 0)
                change = t.get('regularMarketChangePercent', 0)
                
                # Get additional trend data
                volume = t.get('regularMarketVolume', 0)
                market_cap = t.get('marketCap', 0)
                pe_ratio = t.get('trailingPE', 0)
                day_high = t.get('regularMarketDayHigh', 0)
                day_low = t.get('regularMarketDayLow', 0)
                fifty_two_week_high = t.get('fiftyTwoWeekHigh', 0)
                fifty_two_week_low = t.get('fiftyTwoWeekLow', 0)
                
                data_list.append({
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
                })
            except Exception as e:
                print(f"Error fetching data for {symbol}: {e}")
                continue
        
        return sorted(data_list, key=lambda x: x['change'], reverse=True)
    except Exception as e:
        print(f"Error fetching stock data: {e}")
        return []

def get_historical_data(symbol, period="1mo"):
    """Get historical data for trend analysis and chart display"""
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

def get_chart_data(symbol, period="1mo"):
    """Get formatted chart data for different time periods"""
    period_mapping = {
        '1D': '1d',
        '5D': '5d', 
        '1M': '1mo',
        '6M': '6mo',
        'YTD': 'ytd',
        '1Y': '1y',
        '5Y': '5y',
        'Max': 'max'
    }
    
    yf_period = period_mapping.get(period, '1mo')
    
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
        
        return chart_data
    except Exception as e:
        print(f"Error fetching chart data for {symbol}: {e}")
        return []

def get_ticker_suggestions(search_term):
    """Get ticker suggestions based on search term"""
    if not search_term:
        return POPULAR_TICKERS[:10]  # Return top 10 popular tickers
    
    search_term = search_term.upper()
    suggestions = []
    
    # Exact matches first
    for ticker in POPULAR_TICKERS:
        if ticker == search_term:
            suggestions.append(ticker)
    
    # Starts with matches
    for ticker in POPULAR_TICKERS:
        if ticker.startswith(search_term) and ticker not in suggestions:
            suggestions.append(ticker)
    
    # Contains matches
    for ticker in POPULAR_TICKERS:
        if search_term in ticker and ticker not in suggestions:
            suggestions.append(ticker)
    
    return suggestions[:10]  # Return top 10 suggestions

async def handle_toggle_theme(q: Q):
    # Initialize theme if not exists (safety check)
    if not hasattr(q.client, 'theme') or q.client.theme is None:
        q.client.theme = 'h2o-dark'
    
    print(f"Toggling theme. Current: {q.client.theme}")
    
    # Toggle between themes
    old_theme = q.client.theme
    q.client.theme = 'h2o-light' if q.client.theme == 'h2o-dark' else 'h2o-dark'
    
    print(f"Theme toggle: {old_theme} -> {q.client.theme}")
    
    # Preserve current search and chart period
    current_search = q.args.search_ticker if hasattr(q.args, 'search_ticker') else ""
    current_chart_period = q.client.chart_period if hasattr(q.client, 'chart_period') else '1M'
    
    # Update the meta card with new theme
    await update_theme(q)
    
    # Restore search value and chart period if they existed
    if current_search:
        q.args.search_ticker = current_search
    q.client.chart_period = current_chart_period

async def update_theme(q: Q):
    """Update the meta card with the current theme"""
    theme = q.client.theme if hasattr(q.client, 'theme') else 'h2o-dark'
    
    # Define theme-specific colors
    if theme == 'h2o-light':
        bg_color = '#ffffff'
        secondary_bg = '#f5f5f5'
        accent_color = '#1f4e79'
        text_color = '#333333'
        border_color = '#1f4e79'
    else:
        bg_color = '#1a1a1a'
        secondary_bg = '#2d2d2d'
        accent_color = '#f1c232'
        text_color = '#ffffff'
        border_color = '#f1c232'
    
    q.page['active_page_controller'] = ui.meta_card(
        box='activePageController', 
        title='📈 Stock Market Dashboard', 
        refresh=60,
        theme=theme,
        layouts=[
            ui.layout(
                breakpoint='l',
                zones=[
                    ui.zone('header'),
                    ui.zone('content'),
                    ui.zone('footer'),
                ]),
        ],
        stylesheet=ui.inline_stylesheet(f"""
            .ms-Panel {{ background-color: {bg_color} !important; }}
            .ms-Nav {{ background-color: {secondary_bg} !important; }}
            .ms-Button--primary {{ background-color: {accent_color} !important; color: {'#000' if theme == 'h2o-light' else '#000'} !important; }}
            .ms-Button--primary:hover {{ background-color: {'#2c5f99' if theme == 'h2o-light' else '#ffd966'} !important; }}
            .ms-CommandBar {{ background-color: {secondary_bg} !important; }}
            .wave-card {{ border: 1px solid {border_color} !important; }}
            .wave-card-header {{ background-color: {secondary_bg} !important; color: {accent_color} !important; }}
            .ms-DetailsList-headerWrapper {{ background-color: {secondary_bg} !important; }}
            .ms-DetailsHeader {{ color: {accent_color} !important; }}
            .ms-DetailsRow {{ color: {text_color} !important; }}
            .ms-DetailsRow:hover {{ background-color: {'#e6e6e6' if theme == 'h2o-light' else '#333333'} !important; }}
        """)
    )

@app('/stocks')
async def serve(q: Q):
    if not q.client.initialized:
        q.page['active_page_controller'] = ui.meta_card(
            box='activePageController', 
            title='📈 Stock Market Dashboard', 
            refresh=60,
            theme='h2o-dark',
            layouts=[
                ui.layout(
                    breakpoint='l',
                    zones=[
                        ui.zone('header'),
                        ui.zone('content'),
                        ui.zone('footer'),
                    ]),
            ],
            stylesheet=ui.inline_stylesheet("""
                .ms-Panel { background-color: #1a1a1a !important; }
                .ms-Nav { background-color: #2d2d2d !important; }
                .ms-Button--primary { background-color: #f1c232 !important; color: #000 !important; }
                .ms-Button--primary:hover { background-color: #ffd966 !important; }
                .ms-CommandBar { background-color: #2d2d2d !important; }
                .wave-card { border: 1px solid #f1c232 !important; }
                .wave-card-header { background-color: #2d2d2d !important; color: #f1c232 !important; }
                .ms-DetailsList-headerWrapper { background-color: #2d2d2d !important; }
                .ms-DetailsHeader { color: #f1c232 !important; }
                .ms-DetailsRow { color: #ffffff !important; }
                .ms-DetailsRow:hover { background-color: #333333 !important; }
            """)
        )
        q.client.search_symbols = POPULAR_TICKERS.copy()  # Initialize with default stocks
        q.client.chart_period = '1M'  # Default chart period
        q.client.theme = 'h2o-dark'  # Initialize theme
        q.client.initialized = True

    # Handle theme toggle button
    if q.args.toggle_theme:
        await handle_toggle_theme(q)

    # Handle chart period selection
    if q.args.chart_period:
        q.client.chart_period = q.args.chart_period

    # Handle search input
    if q.args.search_ticker:
        search_term = q.args.search_ticker.strip()
        if search_term:
            # Add searched ticker to the list if it's valid
            search_symbols = [search_term.upper()]
            q.client.search_symbols = search_symbols
        else:
            q.client.search_symbols = POPULAR_TICKERS.copy()
    elif q.args.reset_search:
        q.client.search_symbols = POPULAR_TICKERS.copy()

    # Get stock data for current symbols (for search results)
    search_stock_data = get_stock_data(q.client.search_symbols)
    
    # Always get top 5 gainers from default stocks for the gainers section
    default_stock_data = get_stock_data(POPULAR_TICKERS)

    # Get suggestions for autocomplete
    current_search = q.args.search_ticker if q.args.search_ticker else ""
    suggestions = get_ticker_suggestions(current_search)

    # Create header with theme toggle button on the right
    current_theme = q.client.theme if hasattr(q.client, 'theme') else 'h2o-dark'
    theme_icon = '🌞' if current_theme == 'h2o-dark' else '🌙'
    
    q.page['header'] = ui.header_card(
        box='header',
        subtitle="H2O WAVE STOCK APPLICATION",
        icon='TrendingUp',
        title='''📊 Stock Market Dashboard''',
        items=[
            ui.button(
                name='toggle_theme',
                label=f'{theme_icon}',
                tooltip='Switch theme',
                primary=False
            )
        ]
    )

    # Create main content in content zone
    content_items = []
    
    # Search section in content zone
    content_items.extend([
        ui.combobox(
            name='search_ticker',
            label='🔍 Search Stock by Ticker Symbol',
            placeholder='Enter ticker symbol (e.g., AAPL, GOOGL, TSLA)',
            value=current_search,
            choices=[ticker for ticker in suggestions],
            trigger=True
        ),
        ui.button(name='reset_search', label='Show Stocks Info', primary=False),
        ui.separator()
    ])

    if search_stock_data:
        # Check if it's a single stock search to show detailed trend
        is_single_stock = len(q.client.search_symbols) == 1 and q.client.search_symbols != POPULAR_TICKERS
        
        if is_single_stock:
            # Show detailed trend analysis for single stock
            stock = search_stock_data[0]
            symbol = stock['symbol']
            
            # Get historical trend data
            trend_data = get_historical_data(symbol)
            
            # Get chart data and period info
            current_period = q.client.chart_period if hasattr(q.client, 'chart_period') else '1M'
            chart_data = get_chart_data(symbol, current_period)
            
            # Prepare stock info data
            day_range = f"${stock['day_low']:.2f} - ${stock['day_high']:.2f}" if stock['day_low'] > 0 and stock['day_high'] > 0 else "N/A"
            year_range = f"${stock['fifty_two_week_low']:.2f} - ${stock['fifty_two_week_high']:.2f}" if stock['fifty_two_week_low'] > 0 and stock['fifty_two_week_high'] > 0 else "N/A"
            market_cap_formatted = f"${stock['market_cap']/1e9:.2f}B" if stock['market_cap'] > 0 else "N/A"
            volume_formatted = f"{stock['volume']/1e6:.2f}M" if stock['volume'] > 0 else "N/A"
            pe_ratio_formatted = f"{stock['pe_ratio']:.2f}" if stock['pe_ratio'] > 0 else 'N/A'
            
            trend_info = ""
            if trend_data:
                trend_color = '#00ff00' if trend_data['trend_change'] >= 0 else '#ff4444'
                vol_color = '#00ff00' if trend_data['volume_trend'] >= 0 else '#ff4444'
                trend_info = f"1M Trend: {'+' if trend_data['trend_change'] >= 0 else ''}{trend_data['trend_change']:.2f}% | Vol Trend: {'+' if trend_data['volume_trend'] >= 0 else ''}{trend_data['volume_trend']:.1f}%"
            
            # Add stock details to content
            content_items.extend([
                ui.text(f"**📈 {stock['symbol']} - {stock['name']}**"),
                ui.text(f"**Price:** ${stock['price']:.2f} | **Change:** {'+' if stock['change'] >= 0 else ''}{stock['change']:.2f}%"),
                ui.text(f"**Day Range:** {day_range} | **52-Week:** {year_range}"),
                ui.text(f"**Market Cap:** {market_cap_formatted} | **Volume:** {volume_formatted} | **P/E:** {pe_ratio_formatted}"),
                ui.text(f"**{trend_info}**") if trend_info else ui.text(""),
                ui.separator(),
                ui.text('**📈 Chart Time Period**'),
                ui.buttons([
                    ui.button(name='chart_period', value='5D', label='5D', primary=(current_period == '5D')),
                    ui.button(name='chart_period', value='1M', label='1M', primary=(current_period == '1M')),
                    ui.button(name='chart_period', value='6M', label='6M', primary=(current_period == '6M')),
                    ui.button(name='chart_period', value='1Y', label='1Y', primary=(current_period == '1Y')),
                    ui.button(name='chart_period', value='5Y', label='5Y', primary=(current_period == '5Y')),
                    ui.button(name='chart_period', value='Max', label='Max', primary=(current_period == 'Max')),
                ])
            ])
            
            # Add chart to content
            if chart_data and len(chart_data) > 0:
                content_items.extend([
                    ui.text(f'**📊 {symbol} Price Chart ({current_period})**'),
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
                ])
            else:
                content_items.append(ui.text(f'**📊 {symbol} Price Chart ({current_period})** - Chart data unavailable'))

        # Always show top 5 gainers table
        table_data = default_stock_data[:5]  
        
        # Create simple table rows
        table_rows = []
        for stock in table_data:
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
        
        content_items.extend([
            ui.separator(),
            ui.text('**🏆 Top Gainers**'),
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
        ])
    else:
        # Show message when no search data available, but still show top 5 gainers
        if default_stock_data:
            top_5_gainers = default_stock_data[:5]
            
            # Create simple table rows
            table_rows = []
            for stock in top_5_gainers:
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
            
            content_items.extend([
                ui.text('**Search Result Not Found**'),
                ui.text('Unable to fetch data for the searched ticker symbol. Please try a different symbol or check your internet connection.'),
                ui.separator(),
                ui.text('**🏆 Top Gainers**'),
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
            ])

    # Create main content card
    q.page['content'] = ui.form_card(
        box='content',
        items=content_items
    )

    # Add footer
    q.page['footer'] = ui.footer_card(
        box='footer',
        caption='''
        Subavarshana Arumugam
        ©2025 All rights reserved.'''
    )

    await q.page.save()

if __name__ == '__main__':
    main()