from dash import html, callback_context, no_update
from dash.dependencies import Input, Output, State, ALL
from dash_iconify import DashIconify
import dash_mantine_components as dmc
from source.utils import helpers as h
import plotly.graph_objects as go
from source.utils import constants as c
import source.base as b
import json

def register_callbacks(app):
    @app.callback(
        Output('payment_amount', 'error'),
        Output('balance', 'error'),
        Output('interest_rate', 'error'),
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
        # Initialize error values
        payment_amount_error = None
        balance_error = None
        interest_rate_error = None
        
        # Check if balance and payment_amount are filled and valid
        if (len(str(balance).strip()) > 0 
            and len(str(payment_amount).strip()) > 0):
            # Check if payment exceeds balance
            if float(balance) < float(payment_amount):
                payment_amount_error = "The payment amount exceeds the balance"
                balance_error = "The payment amount exceeds the balance"
                
        # Validate interest rate if provided
        if interest_rate is not None and len(str(interest_rate).strip()) > 0:
            # Check if interest rate is within valid range
            if float(interest_rate) <= 0:
                interest_rate_error = "Interest rate must be greater than zero"
            elif float(interest_rate) > 100:
                interest_rate_error = "Interest rate cannot exceed 100%"
        
        # Continue with additional validation if all necessary fields are filled
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
                payment_amount_error = "This payment doesn't cover the interest that accrues each period"
                interest_rate_error = "Payment doesn't cover the interest"
                
        # If validation fails for missing fields, disable submit button
        if not all(i is not None and len(str(i).strip()) > 0 for i in payment_amount_args):
            # Not all payment fields filled
            return payment_amount_error, balance_error, interest_rate_error, True, False
        
        # Check all fields are filled
        all_fields = [name, balance, interest_rate, payment_amount, 
                    payment_frequency, next_payment_date]
        if not all(i is not None and str(i).strip() for i in all_fields):
            # Not all fields filled
            return payment_amount_error, balance_error, interest_rate_error, True, False
        
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
                return payment_amount_error, balance_error, interest_rate_error, True, False
        
        # All validations passed - if we have errors, still disable submit button
        if payment_amount_error or balance_error or interest_rate_error:
            return payment_amount_error, balance_error, interest_rate_error, True, False
        
        # Everything is valid
        return None, None, None, False, True

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

        # IMPORTANT: If the triggered value is None, don't do anything
        # This prevents callbacks from firing when buttons are first created
        if triggered_value == 0:
            return is_open, "", [], form_state
        
        # Add debt button clicked
        if triggered_prop_id == 'open_add_debt_form_button.n_clicks':
            form = h.create_debt_form(mode="add")
            return True, "", form, {'mode': 'add', 'debt_index': None}
        
        # Edit button clicked
        # prop_id format is 
        # {"type":"open_edit_debt_form_button","index":X}.n_clicks
        elif 'open_edit_debt_form_button' in triggered_prop_id:
            try:
                # Extract just the component ID 
                component_id = triggered_prop_id.split('.')[0]
                
                # Parse the JSON string to get the index
                button_dict = json.loads(component_id)
                debt_index = button_dict['index']
                
                # Get debt data from store
                debt_data = debt_details.get(str(debt_index), {})
                
                # Create the form
                form = h.create_debt_form(
                    mode="edit",
                    debt_data=debt_data,
                    debt_index=debt_index
                )
                
                return True, "", form, {'mode': 'edit', 'debt_index': debt_index}
            except Exception as e:
                print(f"ERROR in toggle_debt_form: {e}")
                import traceback
                traceback.print_exc()
        
        # Fallback - no recognized trigger
        return is_open, "", [], form_state
    
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
    def make_graph_and_amortization_table(
        amortizations_data, debt_details_data, name, balance, rate, 
        payment_amount, frequency, next_payment_date, # fig_dict, 
        form_state, n_clicks):
        """
        Creates the debt graph and table views.
        """
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
                    ]), 
                    dmc.Grid([
                        dmc.GridCol(dmc.Text(
                            f"Balance: ${float(balance):,.2f}", 
                            size="xs"
                        ), 
                        span=6), 
                        dmc.GridCol(dmc.Text(
                            f"Rate: {float(rate):,.2f}%", 
                            size="xs"
                            ), 
                        span=6)
                    ]),
                    dmc.Grid([
                        dmc.GridCol(dmc.Text(
                            f"Payment Amount: ${float(payment_amount):,.2f}", 
                            size="xs"
                        ), span=6), 
                        dmc.GridCol(dmc.Text(
                            f"{frequency} Payments", 
                            size="xs"
                        ), span=6)
                    ]),
                    dmc.Grid([
                        dmc.GridCol(dmc.Text(
                            f"Next Payment Date: {next_payment_date}", 
                            size="xs"
                        ), span=12)
                    ])
                ], p="md")
            ], style={"borderColor": debt_color}, withBorder=True),
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
        Output('payoff_graph', 'figure', allow_duplicate=True),
        Input('amortizations-store', 'data'),
        prevent_initial_call=True
    )
    def update_payoff_graph(amortizations_data):
        """Builds the payoff graph from the stored amortization data"""
        # Create a new figure from scratch using the plotly_dark template
        fig = go.Figure(layout=go.Layout(template='plotly_dark'))
        
        if not amortizations_data:
            # Set a title for the empty state but keep the dark theme
            fig.update_layout(
                title='Add a debt to visualize your payoff timeline',
                yaxis_tickprefix='$',
                yaxis_tickformat=',.2f',
                showlegend=False,
            )
            return fig
        
        # Add trace for each debt
        for amort_data in amortizations_data:
            name = amort_data.get('name', 'Unknown Debt')
            debt_color = amort_data.get('color', '#000000')
            raw_data = amort_data.get('raw_data', {})
            
            # Add trace using the raw data (better for numeric operations)
            fig.add_trace(go.Scatter(
                x=raw_data.get('dates', []),
                y=raw_data.get('balances', []),
                line={'color': debt_color},
                name=name
            ))
        
        # Configure layout
        fig.update_layout(
            yaxis_tickprefix='$',
            yaxis_tickformat=',.2f',
            showlegend=False,
            title='Debt Payoff Timeline'
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