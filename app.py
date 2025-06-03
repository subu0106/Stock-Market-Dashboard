"""
Entry Point for Stock Market Dashboard
"""

from h2o_wave import main, ui, Q, app
from src.main import stock_app

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
        from src.utils.helpers import log_error
        log_error(e, "main serve function")
        q.page['content'] = ui.form_card(
            box='content',
            items=[ui.text("Application encountered an unexpected error. Please refresh the page.")]
        )
        await q.page.save()
