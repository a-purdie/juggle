"""Visualization and data display callbacks."""

from dash import html, no_update
from dash.dependencies import Input, Output
import dash_mantine_components as dmc
import plotly.graph_objects as go
from source.utils import constants as c


def register_callbacks(app):
    """Register visualization-related callbacks."""
    
    @app.callback(
        Output('payoff_graph', 'figure', allow_duplicate=True),
        Input('amortizations-store', 'data'),
        prevent_initial_call=True
    )
    def update_payoff_graph(amortizations_data):
        """Builds the payoff graph from the stored amortization data"""
        # Create a new figure from scratch using the plotly_dark template
        fig = go.Figure(layout=go.Layout(template='plotly_dark'))
        
        if not amortizations_data:
            # Configure empty state with minimal margins and no interactions
            fig.update_layout(
                yaxis=dict(
                    tickprefix='$',
                    tickformat='.1f',
                    ticksuffix='K',
                    nticks=5,
                    fixedrange=True
                ),
                xaxis=dict(
                    fixedrange=True
                ),
                showlegend=False,
                margin=dict(l=20, r=10, t=10, b=20)
            )
            return fig
        
        # Add trace for each debt
        for amort_data in amortizations_data:
            name = amort_data.get('name', 'Unknown Debt')
            debt_color = amort_data.get('color', '#000000')
            raw_data = amort_data.get('raw_data', {})
            
            # Add trace using the raw data, converting to thousands for K format
            balances = raw_data.get('balances', [])
            balances_in_thousands = [balance / c.FORMATTING_DIVISOR for balance in balances]
            
            fig.add_trace(go.Scatter(
                x=raw_data.get('dates', []),
                y=balances_in_thousands,
                line={'color': debt_color},
                name=name
            ))
        
        # Configure layout with minimal margins and no interactions
        fig.update_layout(
            yaxis=dict(
                tickprefix='$',
                tickformat='.1f', 
                ticksuffix='K',
                nticks=5,
                fixedrange=True
            ),
            xaxis=dict(
                fixedrange=True
            ),
            showlegend=False,
            margin=dict(l=20, r=10, t=10, b=20)
        )
        
        return fig
    
    @app.callback(
        Output('amortization_schedule', 'children'),
        Input('amortizations-store', 'data'),
        prevent_initial_call=True
    )
    def update_amortization_tables(amortizations_data):
        """
        Builds amortization table components from store data.
        """
        if not amortizations_data:
            return html.Div("No debts added yet.", className="text-center p-3")
        
        amortization_cards = []
        
        for amort_data in amortizations_data:
            name = amort_data.get('name', 'Debt')
            debt_index = amort_data.get('debt_index', 0)
            debt_color = amort_data.get('color', '#000000')
            table_data = amort_data.get('table_data', [])
            columns = amort_data.get('columns', [])
            
            # Create visual component for each amortization
            amortization_card = html.Div([
                dmc.Card([
                    dmc.CardSection([
                        html.H4(name, className='card_title'),
                        html.Hr(),
                        dmc.Table(
                            striped="odd",
                            highlightOnHover=True,
                            withTableBorder=True,
                            withColumnBorders=True,
                            horizontalSpacing="xs",
                            verticalSpacing="xs",
                            className="amortization-table",
                            style={"fontSize": "0.85rem"},
                            children=[
                                html.Thead(
                                    html.Tr([html.Th(col) for col in columns])
                                ),
                                html.Tbody([
                                    html.Tr([
                                        html.Td(row[col]) 
                                        for col in columns
                                    ]) for row in table_data
                                ])
                            ]
                        )
                    ], p="md")
                ], style={"borderColor": debt_color}, withBorder=True),
                html.Hr()],
                id={'type': 'amortization_cards', 'index': debt_index})
                
            amortization_cards.append(amortization_card)
        
        return amortization_cards