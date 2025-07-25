import plotly.express.colors as color
from dash import html
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from source.utils import helpers as h

# The color_order determines the order of colors used in the payoff graph and 
# amortization cards as debts are added
color_order = color.qualitative.Dark24
lighter_color_order = [
    '#d5e9fa', '#f9dfeb', '#c9f6c9'
]

# name_input = h.create_debt_name_input()
# balance_input = h.create_balance_input()
# interest_rate_input = h.create_interest_rate_input()
# payment_amount_input = h.create_payment_amount_input()
# payment_frequency_input = h.create_payment_frequency_input()
# next_payment_date_input = h.create_next_payment_date_input()
# add_debt_button = h.create_add_or_edit_debt_button()

# add_debt_controls = dbc.Card([
#     dbc.CardBody([
#         html.H3("Add Debt", className='card_title'),
#         html.P("All fields are required.", style={'fontSize': 14}),
#         dbc.Form(
#         [name_input, balance_input, interest_rate_input, payment_amount_input, 
#         payment_frequency_input, next_payment_date_input]),
#         html.Hr(),
#         add_debt_button
#     ])
# ])