"""Debt CRUD operation callbacks."""

from dash import html, callback_context, no_update
from dash.dependencies import Input, Output, State, ALL
from dash_iconify import DashIconify
import dash_mantine_components as dmc
from source.utils import helpers as h
from source.utils import constants as c
import source.base as b
import json


def register_callbacks(app):
    """Register debt CRUD-related callbacks."""
    
    @app.callback(
        # Output('payoff_graph', 'figure'),
        Output('amortizations-store', 'data'),
        Output('debt-details-store', 'data'),
        Output('debt_cards_container', 'children'),
        Output('debt_form_drawer', 'opened', allow_duplicate=True),
        [
            State('amortizations-store', 'data'),
            State('debt-details-store', 'data'),
            State('name', 'value'),
            State('balance', 'value'),
            State('interest_rate', 'value'),
            State('payment_amount', 'value'),
            State('payment_frequency', 'value'),
            State('next_payment_date', 'value'),
            # State('payoff_graph', 'figure'),
            State('form-state-store', 'data'),
            Input('submit_debt_form', 'n_clicks')
        ],
        prevent_initial_call=True,
    )
    def make_debt_details_and_amortization_cards(
        amortizations_data, debt_details_data, name, balance, rate, 
        payment_amount, frequency, next_payment_date, # fig_dict, 
        form_state, n_clicks):
        """
        Creates the debt graph and table views.
        """

        # Sanitize the name string
        name = h.sanitize_string(name)
        
        # Check if this is an actual button click or just initialization
        ctx = callback_context
        if not ctx.triggered or n_clicks == 0 or n_clicks is None:
            return no_update, no_update, no_update, no_update
            
        # Validate that all required form fields have values
        if not all([
            name, balance, rate, payment_amount, frequency, next_payment_date
        ]):
            return no_update, no_update, no_update, no_update

        # Initialize store data if None
        if amortizations_data is None:
            amortizations_data = []
        if debt_details_data is None:
            debt_details_data = {}

        # Get form mode and debt index
        mode = form_state.get('mode', 'add')
        debt_index = form_state.get('debt_index')

        if mode == 'add':
            # For add mode, create a new debt index
            current_debt_index = len(debt_details_data)
        else:
            # For edit mode, use the existing debt index
            current_debt_index = debt_index

        debt_color = c.color_order[current_debt_index % len(c.color_order)]
        lighter_debt_color = h.lighten_hex_color(debt_color, amount=0.5)

        amort_object = b.Amortization(
            name=name, account_type='personal', balance=float(balance), 
            interest_rate=float(rate), interest_calculation_method='simple', 
            payment_frequency=frequency, next_payment_date=next_payment_date, 
            payment_amount=float(payment_amount)
        )
        amort_object.generate_amortization()

        amortization_data = {
            'name': name,
            'debt_index': current_debt_index,
            'color': debt_color,
            'raw_data': {
                'dates': list(amort_object.amortization['Payment Date']), 
                'balances': list(amort_object.amortization['Balance Remaining'])
            },
            'table_data': amort_object.pretty_amortization.to_dict('records'),
            'columns': amort_object.pretty_amortization.columns.tolist()
        }

        # Add to amortizations store data
        updated_amortizations = amortizations_data.copy()
        # Find and replace if this debt already exists
        found = False
        for i, item in enumerate(updated_amortizations):
            if item.get('debt_index') == current_debt_index:
                updated_amortizations[i] = amortization_data
                found = True
                break

        # Otherwise append it
        if not found:
            updated_amortizations.append(amortization_data)
        
        debt_details_card = html.Div([
            dmc.Card([
                dmc.CardSection([
                    dmc.Grid([
                        dmc.GridCol(html.H4(
                            name, 
                            className='card_title'), span=9),
                        dmc.GridCol(
                            dmc.Group([
                                dmc.ActionIconGroup([
                                    dmc.ActionIcon(
                                        DashIconify(
                                            icon='iconoir:edit', 
                                            width=20
                                        ),
                                        size='lg',
                                        n_clicks=0,
                                        color="blue",
                                        variant='subtle', 
                                        id={
                                            'type': 'open_edit_debt_form_button', 
                                            'index': current_debt_index
                                            }),
                                    dmc.ActionIcon(
                                        DashIconify(
                                            icon='iconoir:xmark-circle', 
                                            width=20
                                        ),
                                        size='lg',
                                        n_clicks=0,
                                        color='red',
                                        variant='subtle',
                                        id={
                                            'type': 'delete_debt',
                                            'index': current_debt_index
                                            }
                                        ),
                                ])
                            ], justify="flex-end"),
                            span=3
                        )
                    ], gutter="xs"),
                    dmc.Stack([
                        dmc.Text(f"${float(balance):,.2f} Balance with {float(rate):,.2f}% Interest Rate", size="xs"),
                        # dmc.Text(f"Rate: {float(rate):,.2f}%", size="xs"),
                        dmc.Text(f"Paying ${float(payment_amount):,.2f} Every {frequency[:-2]}", size="xs"),
                        # dmc.Text(f"{frequency} Payments", size="xs"),
                        dmc.Text(f"Next Payment On {next_payment_date}", size="xs")
                    ], gap=2)
                ], p="sm")
            ], style={"borderColor": debt_color, "width": "100%", "maxWidth": "calc(100vw - 48px)"}, withBorder=True),
            html.Hr()], 
            id={'type': 'debt_cards', 'index': current_debt_index})
        
        # Add to debt details store data
        updated_debt_details = debt_details_data.copy()
        updated_debt_details[str(current_debt_index)] = {
            'name': name,
            'balance': balance,
            'rate': rate,
            'payment_amount': payment_amount,
            'frequency': frequency,
            'next_payment_date': next_payment_date,
            # 'traces': traces,
            'color': debt_color,
            'card': debt_details_card
        }

        # Create list of debt detail cards from the store data
        debt_detail_cards = []
        for debt_index, debt_data in updated_debt_details.items():
            if 'card' in debt_data:
                debt_detail_cards.append(debt_data['card'])

        return (updated_amortizations, updated_debt_details, 
                debt_detail_cards, False)

    @app.callback(
        Output('amortizations-store', 'data', allow_duplicate=True),
        Output('debt-details-store', 'data', allow_duplicate=True),
        Output('debt_cards_container', 'children', allow_duplicate=True),
        Input({'type': 'delete_debt', 'index': ALL}, 'n_clicks'),
        State('amortizations-store', 'data'),
        State('debt-details-store', 'data'),
        prevent_initial_call=True
    )
    def delete_debt(delete_clicks, amortizations_data, debt_details_data):
        """
        Handles debt deletion when the delete button is clicked.
        Removes the debt from stores and updates UI components.
        """
        ctx = callback_context
        if not ctx.triggered:
            return no_update, no_update, no_update
            
        try:
            # Get the triggered component ID
            triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            # Parse the JSON string to get the debt index
            button_dict = json.loads(triggered_id)
            debt_index = button_dict['index']
            
            # Check if any clicks happened (only needed for the first initialization)
            if not any(click and click > 0 for click in delete_clicks):
                return no_update, no_update, no_update
            
            # Remove the debt from amortizations data
            updated_amortizations = [
                amort for amort in amortizations_data 
                if amort.get('debt_index') != debt_index
            ]
            
            # Remove the debt from debt details data
            updated_debt_details = debt_details_data.copy()
            if str(debt_index) in updated_debt_details:
                del updated_debt_details[str(debt_index)]
            
            # Create updated list of debt cards
            debt_cards = []
            for index, debt_data in updated_debt_details.items():
                if 'card' in debt_data:
                    debt_cards.append(debt_data['card'])
            
            return updated_amortizations, updated_debt_details, debt_cards
            
        except Exception as e:
            print(f"ERROR in delete_debt: {e}")
            import traceback
            traceback.print_exc()
            return no_update, no_update, no_update