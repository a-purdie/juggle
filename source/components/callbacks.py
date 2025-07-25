from dash import html, callback_context, no_update
from dash.dependencies import Input, Output, State, MATCH, ALL
from dash_iconify import DashIconify
import dash_mantine_components as dmc
from source.utils import helpers as h
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from source.utils import constants as c
import source.base as b
import json


#################################################
################### CALLBACKS ###################
#################################################

def register_callbacks(app):
    @app.callback(
        Output('payment_amount', 'invalid'),
        Output('balance', 'invalid'),
        Output('submit_debt_form', 'disabled'),
        Output('submit_debt_form', 'active'),
        [
            Input('name', 'value'),
            Input('balance', 'value'),
            Input('interest_rate', 'value'),
            Input('payment_amount', 'value'),
            Input('payment_frequency', 'value'),
            Input('next_payment_date', 'value'),
            Input('form-state-store', 'data')
        ],
        State('debt-details-store', 'data'),
        prevent_initial_call=True
    )
    def validate_debt_form(
        name, balance, interest_rate, payment_amount, payment_frequency, 
        next_payment_date, form_state, debt_details):
        """
        Validates debt form for both add and edit modes.
        Checks for logical errors and enables/disables the submit button.
        """
        
        # Get form mode and debt index
        mode = form_state.get('mode', 'add')
        debt_index = form_state.get('debt_index')
        
        # Check if all fields have values
        payment_amount_args = [
            balance, interest_rate, payment_amount, payment_frequency
        ]
        
        # Validation logic (same for both modes)
        if all(i is not None and len(str(i)) > 0 for i in payment_amount_args):
            # Calculate period interest
            days = {'Monthly': 31, 'Fortnightly': 14, 'Weekly': 7}
            period_interest = (
                float(balance) 
                * float(interest_rate) 
                * (days[payment_frequency]/36500)
            )
            
            # Check if payment covers interest
            if period_interest > float(payment_amount):
                # Payment doesn't cover interest
                return True, False, True, False
                
            # Check if payment exceeds balance
            if float(balance) < float(payment_amount):
                # Payment exceeds balance
                return False, True, True, False
        else:
            # Not all payment fields filled
            return False, False, True, False
        
        # Check all fields are filled
        all_fields = [name, balance, interest_rate, payment_amount, 
                    payment_frequency, next_payment_date]
        if not all(i is not None and str(i).strip() for i in all_fields):
            # Not all fields filled
            return False, False, True, False
        
        # Additional check for edit mode - has anything changed?
        if mode == 'edit' and debt_index is not None:
            # Get original values
            original_debt = debt_details.get(str(debt_index), {})
            
            # Compare current values with original
            current_values = {
                'name': name,
                'balance': str(balance),
                'rate': str(interest_rate),
                'payment_amount': str(payment_amount),
                'frequency': payment_frequency,
                'next_payment_date': next_payment_date
            }
            
            # Check if any value has changed
            has_changed = False
            for key, current_value in current_values.items():
                # Map keys to match debt_details structure
                original_key = key
                if key == 'rate':
                    original_key = 'rate'
                elif key == 'payment_amount':
                    original_key = 'payment_amount'
                elif key == 'frequency':
                    original_key = 'frequency'
                elif key == 'next_payment_date':
                    original_key = 'next_payment_date'
                    
                original_value = str(original_debt.get(original_key, ''))
                if str(current_value) != original_value:
                    has_changed = True
                    break
            
            if not has_changed:
                # No changes made in edit mode
                return False, False, True, False
        
        # All validations passed
        return False, False, False, True

    # @app.callback(
    #     Output('make_plan_form_collapse', 'opened'),
    #     Input('open_make_plan_form_button', "n_clicks"),
    #     State('make_plan_form_collapse', 'opened'),
    #     prevent_initial_call = True
    # )
    # def toggle_make_plan_form(n_clicks, is_open):
    #     if is_open:
    #         return False
    #     else:
    #         return True

    @app.callback(
        Output('debt_form_drawer', 'opened'),
        Output('debt_form_drawer', 'title'),
        Output('debt_form_drawer', 'children'),
        Output('form-state-store', 'data'),
        [
            Input('open_add_debt_form_button', 'n_clicks'),
            Input({'type': 'open_edit_debt_form_button', 'index': ALL}, 'n_clicks')
        ],
        [
            State('debt_form_drawer', 'opened'),
            State('debt-details-store', 'data'),
            State('form-state-store', 'data')
        ],
        prevent_initial_call=True
    )
    def toggle_debt_form(add_clicks, edit_clicks, is_open, debt_details, form_state):
        """
        Opens/closes the debt form drawer and populates it with either add 
        or edit form
        """
        ctx = callback_context
        if not ctx.triggered:
            return is_open, "", [], form_state
        
        # Get the triggered component's full prop_id
        triggered_prop_id = ctx.triggered[0]['prop_id']
        triggered_value = ctx.triggered[0]['value']
        print(f"DEBUG: triggered_prop_id = {triggered_prop_id}, value = {triggered_value}")

        # IMPORTANT: If the triggered value is None, don't do anything
        # This prevents callbacks from firing when buttons are first created
        if triggered_value == 0:
            return is_open, "", [], form_state
        
        # Add debt button clicked
        if triggered_prop_id == 'open_add_debt_form_button.n_clicks':
            form = h.create_debt_form(mode="add")
            return True, "Add Debt", form, {'mode': 'add', 'debt_index': None}
        
        # Edit button clicked - prop_id format will be: {"type":"open_edit_debt_form_button","index":X}.n_clicks
        elif 'open_edit_debt_form_button' in triggered_prop_id:
            try:
                # Extract just the component ID part (everything before the .n_clicks)
                component_id = triggered_prop_id.split('.')[0]
                
                # Parse the JSON string to get the index
                button_dict = json.loads(component_id)
                debt_index = button_dict['index']
                
                print(f"DEBUG: Extracted debt_index = {debt_index}")
                
                # Get debt data from store
                debt_data = debt_details.get(str(debt_index), {})
                print(f"DEBUG: Debt data = {debt_data}")
                
                # Create the form
                form = h.create_debt_form(
                    mode="edit",
                    debt_data=debt_data,
                    debt_index=debt_index
                )
                
                return True, f"Edit {debt_data.get('name', 'Debt')}", form, {'mode': 'edit', 'debt_index': debt_index}
            except Exception as e:
                print(f"ERROR in toggle_debt_form: {e}")
                import traceback
                traceback.print_exc()
        
        # Fallback - no recognized trigger
        return is_open, "", [], form_state
    
    @app.callback(
        Output('payoff_graph', 'figure'),
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
            State('payoff_graph', 'figure'),
            State('form-state-store', 'data'),
            Input('submit_debt_form', 'n_clicks')
        ],
        prevent_initial_call=True,
    )
    def make_graph_and_amortization_table(
        amortizations_data, debt_details_data, name, balance, rate, 
        payment_amount, frequency, next_payment_date, fig_dict, form_state, n_clicks):
        """
        Creates the debt graph and table views.
        """
        # Check if this is an actual button click or just initialization
        ctx = callback_context
        if not ctx.triggered or n_clicks == 0 or n_clicks is None:
            return no_update, no_update, no_update, no_update, no_update
            
        # Validate that all required form fields have values
        if not all([name, balance, rate, payment_amount, frequency, next_payment_date]):
            return no_update, no_update, no_update, no_update, no_update

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

        x = list(amort_object.amortization['Payment Date'])
        y = list(amort_object.amortization['Balance Remaining'])
        traces = {'x': x, 'y': y}

        amortization_data = {
            'name': name,
            'debt_index': current_debt_index,
            'color': debt_color,
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
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(html.H4(
                            name, 
                            className='card_title'), width=10),
                        dbc.Col(
                            dmc.ActionIcon(
                                DashIconify(icon='iconoir:edit', width=30),
                                size='lg',
                                n_clicks=0,
                                color=lighter_debt_color,
                                variant='subtle', 
                                id={
                                    'type': 'open_edit_debt_form_button', 
                                    'index': current_debt_index
                                    }),
                            width=2)
                        ]), 
                    dbc.Row([
                        dbc.Col(f"Balance: ${float(balance):,.2f}"), 
                        dbc.Col(f"Rate: {float(rate):,.2f}%")], 
                        style={'font-size': 12}),
                    dbc.Row([
                        dbc.Col(f"Payment Amount: ${float(payment_amount):,.2f}"), 
                        dbc.Col(f"{frequency} Payments")],
                        style={'font-size': 12}),
                    dbc.Row(
                        dbc.Col(f"Next Payment Date: {next_payment_date}"),
                        style={'font-size': 12})
                    ])], 
                color=debt_color),
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
            'traces': traces,
            'color': debt_color,
            'card': debt_details_card
        }

        fig = go.Figure(fig_dict)

        fig.add_trace(go.Scatter(
            x=x, 
            y=y,
            line={'color': debt_color},
            name=str(current_debt_index)))

        fig.update_layout(showlegend=False)

        # Create list of debt detail cards from the store data
        debt_detail_cards = []
        for debt_index, debt_data in updated_debt_details.items():
            if 'card' in debt_data:
                debt_detail_cards.append(debt_data['card'])

        return (fig, updated_amortizations, updated_debt_details, 
                debt_detail_cards, False)
        
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
                dbc.Card([
                    dbc.CardBody([
                        html.H4(name, className='card_title'),
                        html.Hr(),
                        dbc.Table(
                            [
                                html.Thead(
                                    html.Tr([html.Th(col) for col in columns])
                                ),
                                html.Tbody([
                                    html.Tr([
                                        html.Td(row[col]) 
                                        for col in columns
                                    ]) for row in table_data
                                ])
                            ],
                            bordered=True, hover=True, responsive=True)
                        ])
                    ], color=debt_color),
                html.Hr()],
                id={'type': 'amortization_cards', 'index': debt_index})
                
            amortization_cards.append(amortization_card)
        
        return amortization_cards