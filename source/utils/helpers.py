from datetime import datetime
import source.base as b
import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify

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

def create_form_field_row(label, component):
    """
    Creates a consistent two-column row for form fields with label on the left
    and the input component on the right.
    """
    return dmc.Grid([
        dmc.GridCol(dmc.Text(label, fw="bold", size="md"), span=4),
        dmc.GridCol(component, span=8)
    ], gutter="xs", mb="sm")

def create_debt_name_input(debt_index=None, value=None):
    id = check_debt_index('name', debt_index)

    name_input = create_form_field_row(
        "Name",
        dmc.TextInput(
            id=id,
            value=value,
            placeholder="Enter debt name",
            styles={"input": {"width": "100%"}}
        )
    )
    
    return name_input

def create_balance_input(debt_index=None, value=None):
    id = check_debt_index('balance', debt_index)

    balance_input = create_form_field_row(
        "Balance",
        dmc.NumberInput(
            id=id,
            value=value,
            step=10,
            min=0,
            max=1000000,  # Maximum value of 1 million
            placeholder="Enter balance amount",
            error=None,  # Will be set by callback
            hideControls=True,  # Hide the increment/decrement controls
            decimalScale=2,  # Show 2 decimal places
            fixedDecimalScale=True,  # Always show 2 decimal places
            prefix="$",  # Add dollar sign prefix
            styles={"input": {"width": "100%"}}
        )
    )
    
    return balance_input

def create_interest_rate_input(debt_index=None, value=None):
    id = check_debt_index('interest_rate', debt_index)

    interest_rate_input = create_form_field_row(
        "Interest Rate",
        dmc.NumberInput(
            id=id,
            value=value,
            step=0.1,
            min=0,
            max=100,  # Maximum interest rate of 100%
            placeholder="Enter interest rate",
            hideControls=True,  # Hide the increment/decrement controls
            decimalScale=3,  # Allow up to 3 decimal places
            fixedDecimalScale=False,  # Don't force showing all 3 decimal places
            suffix="%",  # Add percent sign suffix
            styles={"input": {"width": "100%"}}
        )
    )

    return interest_rate_input

def create_payment_amount_input(debt_index=None, value=None):
    id = check_debt_index('payment_amount', debt_index)

    payment_amount_input = create_form_field_row(
        "Payment Amount",
        dmc.NumberInput(
            id=id,
            value=value,
            step=10,
            min=0,
            max=1000000,  # Maximum value of 1 million
            placeholder="Enter payment amount",
            error=None,  # Error will be set by callback if needed
            hideControls=True,  # Hide the increment/decrement controls
            decimalScale=2,  # Show 2 decimal places
            fixedDecimalScale=True,  # Always show 2 decimal places
            prefix="$",  # Add dollar sign prefix
            styles={"input": {"width": "100%"}}
        )
    )
    
    return payment_amount_input

def create_payment_frequency_input(debt_index=None, value=None):
    id = check_debt_index('payment_frequency', debt_index)
    
    payment_frequency_input = create_form_field_row(
        "Payment Frequency",
        dmc.Select(
            id=id,
            value=value,
            data=["Monthly", "Fortnightly", "Weekly"],
            placeholder="Select payment frequency",
            clearable=False,
            searchable=True,
            styles={"input": {"width": "100%"}}
        )
    )
    
    return payment_frequency_input

def create_next_payment_date_input(debt_index=None, value=None):
    id = check_debt_index('next_payment_date', debt_index)

    next_payment_date_input = create_form_field_row(
        "Next Payment Date",
        dmc.DatePickerInput(
            id=id, 
            value=value,
            minDate=datetime.today(),
            valueFormat='YYYY-MM-DD',
            placeholder="Select next payment date",
            styles={"input": {"width": "100%"}}
        )
    )
    
    return next_payment_date_input

def create_add_or_edit_debt_button(debt_index=None):
    if debt_index is None:
        id = 'add_debt_button'
        button_text = "Add Debt"
    else:
        id = {'type': 'edit_debt_button', 'index': debt_index}
        button_text = "Edit Debt"

    debt_button = dmc.Grid([
        dmc.GridCol(
            dmc.Button(
                button_text, 
                id=id, 
                n_clicks=0, 
                disabled=True),
            span=8,
            offset=2)
    ])
    
    return debt_button

def create_debt_form(mode="add", debt_data=None, debt_index=None):
    """
    Creates a debt form for both adding and editing debts.
    """
    values = {
        'name': debt_data.get('name', '') if debt_data else '',
        'balance': debt_data.get('balance', '') if debt_data else '',
        'rate': debt_data.get('rate', '') if debt_data else '',
        'payment_amount': debt_data.get('payment_amount', '') if debt_data else '',
        'frequency': debt_data.get('frequency', '') if debt_data else '',
        'next_payment_date': debt_data.get('next_payment_date', None) if debt_data else None
    }

    title = "Edit Debt" if mode == "edit" else "Add Debt"
    button_text = "Save Changes" if mode == "edit" else "Add Debt"

    form = dmc.Card([
        dmc.CardSection([
            html.H3(title, className='card_title'),
            dmc.Text("All fields are required.", size="sm", mt="xs", mb="md"),
            dmc.Stack([
                create_debt_name_input(value=values['name']),
                create_balance_input(value=values['balance']),
                create_interest_rate_input(value=values['rate']),
                create_payment_amount_input(value=values['payment_amount']),
                create_payment_frequency_input(value=values['frequency']),
                create_next_payment_date_input(value=values['next_payment_date'])
            ], gap="xs"),
            html.Hr(),
            dmc.Group([
                dmc.Button(
                    button_text,
                    id='submit_debt_form',
                    n_clicks=0,
                    disabled=True,
                    size="md"
                )
            ], justify="center", mb="xs")
        ], p="md")
    ])
    
    return form

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

def create_plans_coming_soon():
    """
    Creates a simple "Coming Soon" placeholder for the Plans tab
    """
    return html.Div([
        dmc.Center([
            dmc.Stack([
                dmc.ThemeIcon(
                    DashIconify(icon="iconoir:rocket", width=40),
                    size=80,
                    radius="xl",
                    variant="light",
                    color="blue"
                ),
                dmc.Title("Coming Soon", order=2),
            ], 
            align="center",
            gap="md",
            style={"padding": "20px"})
        ])
    ], style={"display": "flex", "justifyContent": "center", "marginTop": "40px"})