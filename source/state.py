from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from utils import constants as c

class AppState:
    def __init__(self):
        # Remove instance variables since we'll use dcc.Store instead
        pass
    
    @staticmethod
    def get_store_components():
        """Returns dcc.Store components for state management"""
        return [
            dcc.Store(id='amortizations-store', data=[]),
            dcc.Store(id='debt-details-store', data={})
        ]
    
    @staticmethod
    def get_add_debt_ui():
        """Returns the UI elements for adding debt"""
        return html.Div([
            dbc.Row(
                dbc.Button(
                    "Add new debt",
                    id='openAddDebtFormButton',
                    className='mb-1',
                    n_clicks=0,
                    size='sm', 
                    outline=True, 
                    color='info'
                ), 
                className='col-6 mx-auto p-3'
            ),
            dmc.Drawer(
                c.addDebtControls, 
                id='addDebtFormCollapse', 
                opened=False
            )
        ])

# Helper functions to get initial state values
def get_initial_amortizations():
    """Returns initial empty amortizations list"""
    return []

def get_initial_debt_details():
    """Returns initial empty debt details dictionary"""
    return {}

# Create instance for backwards compatibility (if needed temporarily)
# Remove this once you update all imports in other files
appState = AppState()