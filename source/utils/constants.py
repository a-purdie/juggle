import plotly.express.colors as color
from dash import html
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from utils import helpers as h

# The colorOrder determines the order of colors used in the payoff graph and 
# amortization cards as debts are added
colorOrder = color.qualitative.Dark24
lighterColorOrder = [
    '#d5e9fa', '#f9dfeb', '#c9f6c9'
]

nameInput = h.createDebtNameInput()
balanceInput = h.createBalanceInput()
interestRateInput = h.createInterestRateInput()
paymentAmountInput = h.createPaymentAmountInput()
paymentFrequencyInput = h.createPaymentFrequencyInput()
nextPaymentDateInput = h.createNextPaymentDateInput()
addDebtButton = h.createAddOrEditDebtButton()

addDebtControls = dbc.Card([
    dbc.CardBody([
        html.H3("Add Debt", className = 'card_title'),
        html.P("All fields are required.", style = {'fontSize': 14}),
        dbc.Form(
        [nameInput, balanceInput, interestRateInput, paymentAmountInput, 
        paymentFrequencyInput, nextPaymentDateInput]),
        html.Hr(),
        addDebtButton
    ])
])