"""UI interaction callbacks (drawers, modals, etc.)."""

from dash.dependencies import Input, Output, State
from source.utils import constants as c


def register_callbacks(app):
    """Register UI interaction callbacks."""
    
    @app.callback(
        Output("disclaimer_drawer", "opened"),
        Input("disclaimer_button", "n_clicks"),
        State("disclaimer_drawer", "opened"),
        prevent_initial_call=True
    )
    def toggle_disclaimer_drawer(n_clicks, is_open):
        """Toggle the disclaimer drawer open/closed."""
        if n_clicks:
            return not is_open
        return is_open

    # Clientside callback to auto-scroll to newly added debt cards
    app.clientside_callback(
        f"""
        function(children) {{
            if (children && children.length > 0) {{
                // Small delay to ensure DOM is fully updated
                setTimeout(() => {{
                    // Find all debt cards in the container
                    const debtCards = document.querySelectorAll('[id*="debt_cards"]');
                    if (debtCards.length > 0) {{
                        // Get the last (newest) card
                        const newestCard = debtCards[debtCards.length - 1];
                        // Scroll to it smoothly
                        newestCard.scrollIntoView({{
                            behavior: 'smooth',
                            block: 'nearest',
                            inline: 'start'
                        }});
                    }}
                }}, {c.SCROLL_DELAY_MS});
            }}
            return window.dash_clientside.no_update;
        }}
        """,
        Output('scroll-trigger', 'children'),
        Input('debt_cards_container', 'children'),
        prevent_initial_call=True
    )