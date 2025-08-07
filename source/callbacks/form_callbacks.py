"""Form validation and management callbacks."""

from dash import callback_context, no_update
from dash.dependencies import Input, Output, State, ALL
from source.utils import constants as c
from source.utils import helpers as h
import json


def register_callbacks(app):
    """Register form-related callbacks."""
    
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
            days = c.PAYMENT_FREQUENCY_DAYS
            period_interest = (
                float(balance) 
                * float(interest_rate) 
                * (days[payment_frequency]/c.DAYS_IN_YEAR_FOR_PERCENTAGE)
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