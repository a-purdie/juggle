import dash_bootstrap_components as dbc
from datetime import datetime
import base as b
import dash_mantine_components as dmc

def get_amortization(
        name, account_type, balance, interest_rate, 
        interest_calculation_method, payment_frequency, next_payment_date, 
        payment_amount):
    amort = b.Amortization(
        name, account_type, balance, interest_rate, 
        interest_calculation_method, payment_frequency, 
        next_payment_date, payment_amount)
    amort.generate_amortization()
    return amort

def check_debt_index(field_name, debt_index):
    if debt_index is None:
        id = field_name
    else:
        id = {
            'type': f'edit_{field_name}_input',
            'index': debt_index
            }
    return id

def create_debt_name_input(debt_index=None, value=None):
    id = check_debt_index('name', debt_index)

    name_input = dbc.Row([
    dbc.Label(
        "Name", 
        html_for=id, 
        width=5, 
        style={'font-size': 16}),
    dbc.Col(dbc.Input(
            id=id,
            value=value), 
            width=7)], 
        className='mb-1') 
    
    return name_input

def create_balance_input(debt_index=None, value=None):
    id = check_debt_index('balance', debt_index)

    balance_input = dbc.Row([
        dbc.Label(
            "Balance", 
            html_for=id, 
            width=5, 
            style={'font-size': 16}),
        dbc.Col(dbc.InputGroup([
            dbc.InputGroupText("$"), 
            dbc.Input(id=id, value=value),
            dbc.FormFeedback(
                'The payment amount exceeds the balance.', type='invalid'
            )]), width=7)], className='mb-1')
    
    return balance_input

def create_interest_rate_input(debt_index=None, value=None):
    id = check_debt_index('interest_rate', debt_index)

    interest_rate_input = dbc.Row([
    dbc.Label(
        "Interest Rate", 
        html_for=id, 
        width=5, 
        style={'font-size': 16}),
    dbc.Col(dbc.InputGroup([
        dbc.Input(id=id, value=value), 
        dbc.InputGroupText('%')]), width=7)], className='mb-1')

    return interest_rate_input

def create_payment_amount_input(debt_index=None, value=None):
    id = check_debt_index('payment_amount', debt_index)

    payment_amount_input = dbc.Row([
        dbc.Label(
            "Payment Amount", 
            html_for=id, 
            width=5, 
            style={'font-size': 16}),
        dbc.Col(dbc.InputGroup([
            dbc.InputGroupText("$"), 
            dbc.Input(id=id, value=value),
            dbc.FormFeedback(
                ('This payment amount does not cover the amount of interest '
                'that accrues each bill cycle'), 
                type='invalid')]), width=7)], className='mb-1')
    
    return payment_amount_input

def create_payment_frequency_input(debt_index=None, value=None):
    id = check_debt_index('payment_frequency', debt_index)
    
    payment_frequency_input = dbc.Row([
        dbc.Label(
            "Frequency", 
            html_for=id, 
            width=5, 
            style={'font-size': 16}),
        dbc.Col(dbc.Select(
            id=id, value=value,
            options=[{"label": "Monthly", "value": "Monthly"},
                     {"label": "Fortnightly", "value": "Fortnightly"},
                     {"label": "Weekly", "value": "Weekly"}]), 
            width=7)], className='mb-1')

    return payment_frequency_input

def create_next_payment_date_input(debt_index=None, value=None):
    id = check_debt_index('next_payment_date', debt_index)

    next_payment_date_input = dbc.Row([
    dbc.Label(
        "Next Payment", 
        html_for=id, 
        width=5, 
        style={'font-size': 16}),
    dbc.Col(dmc.DatePickerInput(
        id=id, value=value,
        minDate=datetime.today(),
        valueFormat='YYYY-MM-DD'), width=7)], className='mb-1')
    
    return next_payment_date_input

def create_add_or_edit_debt_button(debt_index=None):
    if debt_index is None:
        id = 'add_debt_button'
        button_text = "Add Debt"
    else:
        id = {'type': 'edit_debt_button', 'index': debt_index}
        button_text = "Edit Debt"

    debt_button = dbc.Row([
        dbc.Button(
            button_text, 
            id=id, 
            n_clicks=0, 
            disabled=True)],
        className='col-8 mx-auto')
    
    return debt_button

def create_debt_form(mode="add", debt_data=None, debt_index=None):
    pass

def lighten_hex_color(hex_code, amount=0.5):
    """
    From a hex code, convert to RGB, blend with white, and return the 
    lightened color's hex code.
    """
    hex_code = hex_code.lstrip('#')
    r = int(hex_code[0:2], 16)
    g = int(hex_code[2:4], 16)
    b = int(hex_code[4:6], 16)

    r = int(r + (255 - r) * amount)
    g = int(g + (255 - g) * amount)
    b = int(b + (255 - b) * amount)

    return '#{:02x}{:02x}{:02x}'.format(r, g, b)