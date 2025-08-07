from datetime import datetime
import source.base as b
import dash_mantine_components as dmc
import dash.html
from dash_iconify import DashIconify
import html
import re
from source.utils import constants as c

def sanitize_string(value, max_length=100):
    if not value:
        return ""
    value = html.escape(str(value))
    value = re.sub(r'[^\x20-\x7E]', '', value)
    return value[:max_length]
    
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


def create_form_field(field_type, field_name, label, debt_index=None, value=None, **kwargs):
    """
    Generic factory function to create form fields with consistent structure.
    
    Args:
        field_type: Type of input ('text', 'number', 'select', 'date')
        field_name: The field name for ID generation
        label: Display label for the field
        debt_index: Optional debt index for edit mode
        value: Initial value for the field
        **kwargs: Additional props to pass to the component
    """
    field_id = check_debt_index(field_name, debt_index)
    
    # Default styles for all inputs
    default_styles = {"input": {"width": "100%"}}
    styles = kwargs.pop('styles', default_styles)
    
    if field_type == 'text':
        component = dmc.TextInput(
            id=field_id,
            value=value,
            styles=styles,
            **kwargs
        )
    elif field_type == 'number':
        component = dmc.NumberInput(
            id=field_id,
            value=value,
            hideControls=True,
            styles=styles,
            **kwargs
        )
    elif field_type == 'select':
        component = dmc.Select(
            id=field_id,
            value=value,
            clearable=False,
            searchable=True,
            styles=styles,
            **kwargs
        )
    elif field_type == 'date':
        component = dmc.DatePickerInput(
            id=field_id,
            value=value,
            styles=styles,
            **kwargs
        )
    else:
        raise ValueError(f"Unsupported field_type: {field_type}")
    
    return create_form_field_row(label, component)

def create_debt_name_input(debt_index=None, value=None):
    """Create debt name text input field."""
    return create_form_field(
        'text', 'name', 'Name', 
        debt_index=debt_index, 
        value=value,
        placeholder="Enter debt name"
    )

def create_balance_input(debt_index=None, value=None):
    """Create balance number input field."""
    return create_form_field(
        'number', 'balance', 'Balance',
        debt_index=debt_index,
        value=value,
        step=10,
        min=0,
        max=c.MAX_DEBT_BALANCE,
        placeholder="Enter balance amount",
        error=None,
        decimalScale=2,
        fixedDecimalScale=True,
        prefix="$"
    )

def create_interest_rate_input(debt_index=None, value=None):
    """Create interest rate number input field."""
    return create_form_field(
        'number', 'interest_rate', 'Interest Rate',
        debt_index=debt_index,
        value=value,
        step=0.1,
        min=0,
        max=c.MAX_INTEREST_RATE,
        placeholder="Enter interest rate",
        decimalScale=3,
        fixedDecimalScale=False,
        suffix="%"
    )

def create_payment_amount_input(debt_index=None, value=None):
    """Create payment amount number input field."""
    return create_form_field(
        'number', 'payment_amount', 'Payment Amount',
        debt_index=debt_index,
        value=value,
        step=10,
        min=0,
        max=c.MAX_DEBT_BALANCE,
        placeholder="Enter payment amount",
        error=None,
        decimalScale=2,
        fixedDecimalScale=True,
        prefix="$"
    )

def create_payment_frequency_input(debt_index=None, value=None):
    """Create payment frequency select input field."""
    return create_form_field(
        'select', 'payment_frequency', 'Payment Frequency',
        debt_index=debt_index,
        value=value,
        data=c.PAYMENT_FREQUENCY_OPTIONS,
        placeholder="Select payment frequency"
    )

def create_next_payment_date_input(debt_index=None, value=None):
    """Create next payment date picker input field."""
    return create_form_field(
        'date', 'next_payment_date', 'Next Payment Date',
        debt_index=debt_index,
        value=value,
        minDate=datetime.today().strftime('%Y-%m-%d'),
        valueFormat='YYYY-MM-DD',
        placeholder="Select next payment date"
    )

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
            dash.html.H3(title, className='card_title'),
            dmc.Text("All fields are required.", size="sm", mt="xs", mb="md"),
            dmc.Stack([
                create_debt_name_input(value=values['name']),
                create_balance_input(value=values['balance']),
                create_interest_rate_input(value=values['rate']),
                create_payment_amount_input(value=values['payment_amount']),
                create_payment_frequency_input(value=values['frequency']),
                create_next_payment_date_input(value=values['next_payment_date'])
            ], gap="xs"),
            dash.html.Hr(),
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
    return dash.html.Div([
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