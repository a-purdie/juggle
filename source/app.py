import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import Dash, html, dcc, _dash_renderer
import pandas as pd
import plotly.graph_objects as go
import plotly.express.colors as color
from utils import constants as c
from components import callbacks as cb

externalStylesheets = [
    "https://fonts.googleapis.com/css2?family=Chonburi&display=swap",
    "/assets/bootstrap.css",
    "/assets/fontawesome/css/fontawesome.css",
    "/assets/fontawesome/css/solid.css",
    dmc.styles.ALL,
    dmc.styles.DATES
]

app = Dash(external_stylesheets = externalStylesheets)
_dash_renderer._set_react_version('18.2.0')
app.title = 'indentured.services - Debt Calculator'

# debtDetails is a dictionary that holds all the debts that have been added by 
# the user so far. Its keys are sequential, non-negative integers that increment 
# by one when a new debt is added, and its values are also dictionaries with three
# key-value pairs. The inner dictionary's keys are "name", "amortization" 
# and "traces". The "name" item contains the name of the debt provided by 
# the user. The "amortization" item holds the amortization table components 
# that are printed to the table view. The "traces" item holds another dictionary 
# containing the details needed to add a trace to the payoff graph. The keys 
# of the traces dictionary are "x", "y", representing the x and y coordinates 
# of the amortization schedule.

# plans is a dictionary that holds all the details about user specified payoff 
# plans. Plans can be one of three types:
### 1) Minimum payments only; payment amounts remain the same for all debts
###    across time, aside from user created rules
### 2) Snowball; payment amounts are added to the next highest balance as debt 
###    is paid off
### 3) Avalanche; payment amounts are added to the next highest interest rate 
###    as debt is paid off
# Within each plan, the user can specify rules. A rule specifies one or more 
# payments beyond the minimum payment (paymentAmount) on a single debt. The 
# attributes of a rule are 
### 1) name
### 2) amount
### 3) one time payment or multiple payments indicator
### 4) start date
### 5) end date (only applies when the rule contains multiple payments)+
### 6) debt (pick from the debt's the user has added or choose to follow the 
###    payoff strategy specified by the plan type)
# The plans dictionary contains one key-value pair for each plan defined by 
# the user, where the key is the name of the plan. Each plan is another 
# dictionary with two key-value pairs. The first key is 'type' and specifies 
# the payoff strategy (minimum, snowball, or avalanche). The second key is 
# 'rules', which specifies the user defined rules. The value of the 'rules' 
# pair is another dictionary, with keys set to rule names. The value of each 
# rule is yet another dictionary that specify items 2 - 6 from the description 
# of rules above. So as an example:

# plans = {
#     'My Plan': {
#         {
#             'type': 'avalanche',
#             'rules': {
#                 'My First Rule': {
#                     'amount': 500,
#                     'singleOrMultiple': 'multiple',
#                     'startDate': '2025-01-31',
#                     'endDate': '2026-01-31',
#                     'debt': 'strategy'
#                 }
#             }
#         }
# }}

# This user would have a single plan in the Plans tab called "My Plan" with 
# the avalanche payoff strategy. It would have a single rule that would apply 
# an additional $500.00 payment to the debt consistent with the plan's payoff 
# strategy for one year, i.e., to the debt with the highest interest rate.

plans = {}

# Specifies the order of color assignment of the lines and debt cards
colorOrder = color.qualitative.Dark24
lighterColorOrder = [
    '#d5e9fa', '#f9dfeb', '#c9f6c9'
]
debtCount = 0

#################################################
######### ADD PLANS FORM AND CONTROLS ###########
#################################################

planNameInput = dbc.Row([
    dbc.Label("Plan Name", html_for = 'planName', width = 5, style = {'font-size': 16}),
    dbc.Col(dbc.Input(id = 'planName'), width = 7)], className = 'mb-1')

infoIcon = html.I(
    className = 'fa-solid fa-circle-info', 
    style = {'color': '#aaaaaa'})

planTypeInfo = [
    dmc.Text("Avalanche", fw = 700), 
    dmc.Text((
    "Favors debts with the highest interest rate. When an account is paid off, "
    "the minimum payment used to pay that account is allocated to the unpaid "
    "debt with the highest interest rate. This method costs the least and pays "
    "off debt the fastest."), size = 'sm'),
    dmc.Text("Snowball", fw = 700),
    dmc.Text((
    "Favors debts with the lowest balance. "
    "Like avalanche, only the extra payments go to the debt with the "
    "lowest balance. This method costs more, but some people "
    "appreciate the psychological boost of paying off entire accounts "
    "faster at the beginning."), size = 'sm'),
    dmc.Text("Minimum Payments Only", fw = 700),
    dmc.Text((
    "Pay only the minimum amount due on each debt. When an account is paid "
    "off, the minimum payment used to pay that account is not allocated to any "
    "other unpaid debt. This method takes the longest, costs the most, and "
    "isn't generally recommended."), size = 'sm')]

planTypeRadioOptions = [
    {"label": "Avalanche", "value": 'avalanche'},
    {"label": "Snowball", "value": 'snowball'},
    {"label": "Minimum Payments Only", "value": 'minimum'}]


planTypeRadio = dbc.Row([
        dbc.Col(dmc.HoverCard(
            width = 300,
            position = 'right',
            transitionProps = {
                "transition": "slide-right", 
                "duration": 400,
                "timingFunction": "ease"},
            withArrow = True,
            children = [
                dmc.HoverCardTarget(["Plan Type ", infoIcon]),
                dmc.HoverCardDropdown(planTypeInfo)
            ]
        ), width = 5),
    dbc.Col(dbc.RadioItems(
            options = planTypeRadioOptions,
            id = "planType"
        ), width = 7)
])

addPlanButton = dbc.Row([
    dbc.Button("Add Plan", id = 'addPlan', n_clicks = 0, disabled = True)],
    className = 'col-8 mx-auto')

addPlanControls = dbc.Card([
    dbc.CardBody([
        html.H3("Make a Plan", className = 'card_title'),
        dbc.Form(
        [planNameInput, planTypeRadio]),
        html.Hr(),
        addPlanButton])])

#################################################
################## PLANS TAB ####################
#################################################

addPlanDetails = [
    html.Div(
        [dbc.Row(
            dbc.Button(
                "Make a plan",
                id = 'openMakePlanFormButton',
                className = 'mb-1',
                n_clicks = 0,
                size = 'sm', outline = True, color = 'info'
            ), className = 'col-6 mx-auto p-3'),
            dmc.Drawer(
                addPlanControls, 
                id = 'makePlanFormCollapse', 
                opened = False)
        ]),
    html.Br()
    ]

#################################################
####### GRAPH AND SCHEDULE VIEW CONTENT #########
#################################################

graphViewContent = dbc.Col(dcc.Graph(
        figure = go.Figure(
            data = go.Scatter(), 
            layout = go.Layout(
                template = 'plotly_dark',
                yaxis_tickprefix = '$', yaxis_tickformat = ',.2f')),
        id = 'payoffGraph', 
        style = {'width': '72vw', 'height': '70vh'}), 
    width = 8)

df = pd.DataFrame(columns = ['paymentDate', 'paymentAmount', 'interestAmount', 
                'principalAmount', 'remainingBalance'])

amortizationViewContent = dbc.Col(
    [], id='amortizationSchedule', width=12)

#################################################
## DEBT DETAILS AND PLAN DETAILS VIEW CONTENT ###
#################################################

# Separate container for debt cards
debtCardsContainer = html.Div(
    [], 
    id='debtCardsContainer',
    style={'maxHeight': '70vh', 'overflow': 'scroll'}
)

# Main debt details view with fixed button and scrollable cards area
debtDetailsViewContent = dbc.Col([
    # Fixed "Add new debt" button at the top
    dbc.Row(
        dbc.Button(
            "Add new debt",
            id='openAddDebtFormButton',
            className='mb-1',
            n_clicks=0,
            size='sm', 
            outline=True, 
            color='info'
        ), 
        className='col-6 mx-auto p-3'
    ),
    # Debt cards container below the button
    debtCardsContainer,
    # Drawer for add debt form
    dmc.Drawer(
        c.addDebtControls, 
        id='addDebtFormCollapse', 
        opened=False
    )
])

planDetailsViewContent = dbc.Col(
    addPlanDetails, id='planDetailsView', width=12)

#################################################
#################### LAYOUT #####################
#################################################

app.layout = dmc.MantineProvider([
    dcc.Store(id='amortizations-store', data=[]),
    dcc.Store(id='debt-details-store', data={}),
    # Main app container
    dbc.Container([
        html.H1("indentured.services", style={'font-family': 'Chonburi'}),
        html.P(
            "Break the chains of your peonage and claim delicious freedom at last",
            style={'fontSize': 10}),
        html.Hr(),
        dbc.Row([
                dbc.Col(
                    dbc.Tabs([
                        dbc.Tab(debtDetailsViewContent, label='Debt Details'),
                        dbc.Tab(planDetailsViewContent, label='Plans')]), 
                    width=3),
                dbc.Col(
                    dbc.Tabs([
                        dbc.Tab(graphViewContent, label="Graph View"), 
                        dbc.Tab(amortizationViewContent, label="Table View")]), 
                        width=9)
                ]
            )
        ])
    ],
    forceColorScheme='dark')

#################################################
###################### RUN ######################
#################################################

cb.register_callbacks(app)

if __name__ == '__main__':
    app.run(debug = True)
    # app.run_server(debug = True, port = 8050, host = "0.0.0.0")
