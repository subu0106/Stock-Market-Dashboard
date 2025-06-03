"""
Theme Management for Stock Market Dashboard
Handles theme switching and styling for the H2O Wave stock application.
"""

from h2o_wave import Q, ui
from ..config.constants import THEMES, DEFAULT_SETTINGS


async def handle_toggle_theme(q: Q) -> None:
    """Handle theme toggle button click with immediate response."""
    if not hasattr(q.client, 'theme') or q.client.theme is None:
        q.client.theme = 'h2o-dark'
    
    old_theme = q.client.theme
    q.client.theme = 'h2o-light' if q.client.theme == 'h2o-dark' else 'h2o-dark'
    
    await update_theme_immediately(q)


async def update_theme_immediately(q: Q) -> None:
    """Update only the theme styling without re-rendering content."""
    theme = q.client.theme if hasattr(q.client, 'theme') else 'h2o-dark'
    theme_config = THEMES.get(theme, THEMES['h2o-dark'])
    
    q.page['active_page_controller'] = ui.meta_card(
        box='activePageController', 
        title='📈 Stock Market Dashboard', 
        refresh=DEFAULT_SETTINGS['refresh_interval'],
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
            .ms-Panel {{ background-color: {theme_config['bg_color']} !important; }}
            .ms-Nav {{ background-color: {theme_config['secondary_bg']} !important; }}
            .ms-Button--primary {{ background-color: {theme_config['accent_color']} !important; color: {theme_config['button_text_color']} !important; }}
            .ms-Button--primary:hover {{ background-color: {theme_config['button_hover_color']} !important; }}
            .ms-CommandBar {{ background-color: {theme_config['secondary_bg']} !important; }}
            .wave-card {{ border: 1px solid {theme_config['border_color']} !important; }}
            .wave-card-header {{ background-color: {theme_config['secondary_bg']} !important; color: {theme_config['accent_color']} !important; }}
            .ms-DetailsList-headerWrapper {{ background-color: {theme_config['secondary_bg']} !important; }}
            .ms-DetailsHeader {{ color: {theme_config['accent_color']} !important; }}
            .ms-DetailsRow {{ color: {theme_config['text_color']} !important; }}
            .ms-DetailsRow:hover {{ background-color: {theme_config['row_hover_color']} !important; }}
        """)
    )
    
    await q.page.save()


def initialize_theme(q: Q) -> None:
    """Initialize the default theme for a new client session."""
    default_theme = THEMES['h2o-dark']
    
    q.page['active_page_controller'] = ui.meta_card(
        box='activePageController', 
        title='📈 Stock Market Dashboard', 
        refresh=DEFAULT_SETTINGS['refresh_interval'],
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
        stylesheet=ui.inline_stylesheet(f"""
            .ms-Panel {{ background-color: {default_theme['bg_color']} !important; }}
            .ms-Nav {{ background-color: {default_theme['secondary_bg']} !important; }}
            .ms-Button--primary {{ background-color: {default_theme['accent_color']} !important; color: {default_theme['button_text_color']} !important; }}
            .ms-Button--primary:hover {{ background-color: {default_theme['button_hover_color']} !important; }}
            .ms-CommandBar {{ background-color: {default_theme['secondary_bg']} !important; }}
            .wave-card {{ border: 1px solid {default_theme['border_color']} !important; }}
            .wave-card-header {{ background-color: {default_theme['secondary_bg']} !important; color: {default_theme['accent_color']} !important; }}
            .ms-DetailsList-headerWrapper {{ background-color: {default_theme['secondary_bg']} !important; }}
            .ms-DetailsHeader {{ color: {default_theme['accent_color']} !important; }}
            .ms-DetailsRow {{ color: {default_theme['text_color']} !important; }}
            .ms-DetailsRow:hover {{ background-color: {default_theme['row_hover_color']} !important; }}
        """)
    )


def get_current_theme(q: Q) -> str:
    """Get the current theme for the client session."""
    return q.client.theme if hasattr(q.client, 'theme') else 'h2o-dark'
