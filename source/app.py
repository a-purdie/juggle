import dash_mantine_components as dmc
from dash import Dash, html, dcc, _dash_renderer
import os
from flask import make_response
from functools import wraps
from dash_iconify import DashIconify
import pandas as pd
import plotly.graph_objects as go
from source.components import callbacks as cb
from source.utils.helpers import create_plans_coming_soon

external_stylesheets = [
    "https://fonts.googleapis.com/css2?family=Chonburi&display=swap",
    "assets/bootstrap.css",
    "assets/fontawesome/css/fontawesome.css",
    "assets/fontawesome/css/solid.css",
    "assets/custom.css",
    "assets/table-styles.css",
    "assets/responsive.css",
    dmc.styles.ALL,
    dmc.styles.DATES
]

app = Dash(
    external_stylesheets=external_stylesheets,
    # assets_folder='./source/assets'
)
app.config.suppress_callback_exceptions = True  # To handle dynamic components
server = app.server
_dash_renderer._set_react_version('18.2.0')
app.title = 'indentured.services - Debt Calculator'

disclaimer_content = [
    dmc.Title("Disclaimer", order=3, mb="md"), 
    dmc.Text(
        "This application does not provide financial advice. The payoff "
        "graphs, amortization tables, and financial projections provided "
        "are for informational purposes only. The projections are only "
        "estimates based on the information you provide and standard " 
        "financial formulas. They are not guarantees of when or how your "
        "debt will be paid off.", size="xs"
    ), 
    html.Br(),
    dmc.Text(
        "Your actual results could vary due to changes in interest rates, "
        "payment schedules, additional fees assessed by lenders, or any one "
        "of the myriad other factors not explicitly accounted for by this "
        "application. Financial decisions should not be made solely on the "
        "basis of the projections provided here.", size="xs"
    ), 
    html.Br(),
    dmc.Text(
        "The free services provided by this app are offered as is and are not "
        "financial advice. By using the app, you assume full liability for "
        "any damages, financial or otherwise, that you or others incur as a "
        "result of your use of the app.", size="xs"
    )
]

plans = {}

#################################################
######### ADD PLANS FORM AND CONTROLS ###########
#################################################

plan_name_input = dmc.Grid([
    dmc.GridCol(
        dmc.Text("Plan Name", fw="bold", style={'fontSize': 16}),
        span=5
    ),
    dmc.GridCol(
        dmc.TextInput(id='plan_name'),
        span=7
    )],
    gutter="md",
    mb="xs"
)

info_icon = html.I(
    className='fa-solid fa-circle-info', 
    style={'color': '#aaaaaa'})

plan_type_info = [
    dmc.Text("Avalanche", fw="bold"), 
    dmc.Text((
    "Favors debts with the highest interest rate. When an account is paid off, "
    "the minimum payment used to pay that account is allocated to the unpaid "
    "debt with the highest interest rate. This method costs the least and pays "
    "off debt the fastest."), size='sm'),
    dmc.Text("Snowball", fw="bold"),
    dmc.Text((
    "Favors debts with the lowest balance. "
    "Like avalanche, only the extra payments go to the debt with the "
    "lowest balance. This method costs more, but some people "
    "appreciate the psychological boost of paying off entire accounts "
    "faster at the beginning."), size='sm'),
    dmc.Text("Minimum Payments Only", fw="bold"),
    dmc.Text((
    "Pay only the minimum amount due on each debt. When an account is paid "
    "off, the minimum payment used to pay that account is not allocated to any "
    "other unpaid debt. This method takes the longest, costs the most, and "
    "isn't generally recommended."), size='sm')]

plan_type_radio_options = [
    {"label": "Avalanche", "value": 'avalanche'},
    {"label": "Snowball", "value": 'snowball'},
    {"label": "Minimum Payments Only", "value": 'minimum'}]


plan_type_radio = dmc.Grid([
        dmc.GridCol(dmc.HoverCard(
            width=300,
            position='right',
            withArrow=True,
            children=[
                dmc.HoverCardTarget(["Plan Type ", info_icon]),
                dmc.HoverCardDropdown(plan_type_info)
            ]
        ), span=5),
    dmc.GridCol(dmc.RadioGroup(
            id="plan_type",
            children=[
                dmc.Radio(label="Avalanche", value="avalanche"),
                dmc.Radio(label="Snowball", value="snowball"),
                dmc.Radio(label="Minimum Payments Only", value="minimum")
            ]
        ), span=7)
], gutter="md")

add_plan_button = dmc.Grid([
    dmc.GridCol(
        dmc.Button("Add Plan", id='add_plan', n_clicks=0, disabled=True),
        span=8,
        offset=2
    )])

add_plan_controls = dmc.Card([
    dmc.CardSection([
        html.H3("Make a Plan", className='card_title'),
        dmc.Stack(
        [plan_name_input, plan_type_radio]),
        html.Hr(),
        add_plan_button
    ], p="md")
])

#################################################
################## PLANS TAB ####################
#################################################


# Create plan details view with Coming Soon component
plan_details_view_content = dmc.GridCol(
    create_plans_coming_soon(), id='plan_details_view', span=12)

#################################################
####### GRAPH AND SCHEDULE VIEW CONTENT #########
#################################################

graph_view_content = dmc.GridCol(dcc.Graph(
        figure=go.Figure(
            data=go.Scatter(), 
            layout=go.Layout(
                template='plotly_dark',
                yaxis_tickprefix='$', 
                yaxis_tickformat=',.2f',
                margin=dict(l=40, r=40, t=60, b=40) # Reduce margins for more space
            )),
        id='payoff_graph', 
        style={'width': '100%', 'height': 'calc(95vh - 150px)'}, # Dynamic height based on viewport
        config={'responsive': True, 'displayModeBar': False}), 
    )

df = pd.DataFrame(columns=['paymentDate', 'paymentAmount', 'interestAmount', 
                'principalAmount', 'remainingBalance'])

amortization_view_content = dmc.GridCol(
    [], id='amortization_schedule', span=12)

#################################################
## DEBT DETAILS AND PLAN DETAILS VIEW CONTENT ###
#################################################

debt_form_drawer = dmc.Drawer(
    id='debt_form_drawer',
    title="",
    opened=False,
    children=[]
)

# Separate container for debt cards
debt_cards_container = html.Div(
    [], 
    id='debt_cards_container',
    className='debt-cards-container',
    style={
        'maxHeight': 'calc(95vh - 180px)',
        'overflowY': 'auto',  # Show scrollbar only when its needed
        'scrollbarWidth': 'thin', # Thinner scrollbar for Firefox users
        'msOverflowStyle': 'none', # Hide scrollbar in Edge
    }
)

# Main debt details view with fixed button and scrollable cards area
debt_details_view_content = dmc.GridCol([
    dmc.Grid([
        dmc.GridCol(
            dmc.Button(
                "Add new debt",
                id='open_add_debt_form_button',
                variant="outline",
                color="blue",
                size="sm",
                n_clicks=0
            ),
            span=6,
            offset=3,
            py="xs"
        )
    ]),
    # Debt cards container below the button
    debt_cards_container,
    # Drawer for add debt form
    debt_form_drawer
])

plan_details_view_content = dmc.GridCol(
    create_plans_coming_soon(), id='plan_details_view', span=12)

#################################################
#################### LAYOUT #####################
#################################################

disclaimer_drawer = dmc.Drawer(
    id="disclaimer_drawer",
    title="",
    size="md",
    position="right",
    opened=False,
    children=disclaimer_content
)

app.layout = dmc.MantineProvider([
    disclaimer_drawer,
    dcc.Store(id='amortizations-store', data=[]),
    dcc.Store(id='debt-details-store', data={}),
    dcc.Store(id='form-state-store', data={'mode': 'add', 'debt_index': None}),
    html.Div(id='scroll-trigger', style={'display': 'none'}),  # Dummy div for clientside callback
    # Main app container
    dmc.Container([
        dmc.Grid([
            dmc.GridCol([
                html.H1("indentured.services", style={'font-family': 'Chonburi'}),
                html.P(
                    "Break the chains of your peonage and claim delicious freedom at last",
                    style={'fontSize': 10}),
            ], span={'base': 8, 'md': 10}),
            dmc.GridCol([
                dmc.Group([
                    dmc.Button(
                        "Disclaimer",
                        id="disclaimer_button",
                        variant="subtle",
                        size="xs",
                        color="gray",
                        n_clicks=0
                    ),
                    html.A(
                        dmc.ActionIcon(
                            DashIconify(
                                icon="mdi:github", 
                                width=30
                            ), 
                            size="lg",
                            variant="subtle",
                            color="gray"
                        ),
                        href="https://github.com/a-purdie/juggle",
                        target="_blank"
                    )
                ], justify="center", wrap="nowrap"),
            ], span={'base': 4, 'md': 2}, style={"textAlign": "center"}),
        ]),
        html.Hr(),
        dmc.Grid([
                dmc.GridCol(
                    dmc.Tabs(
                        [
                            dmc.TabsList([
                                dmc.TabsTab(
                                    "Debt Details", 
                                    value="debt_details"
                                    ),
                                dmc.TabsTab(
                                    "Plans", 
                                    value="plans"
                                    ),
                            ]),
                            dmc.TabsPanel(
                                debt_details_view_content, 
                                value="debt_details"
                                ),
                            dmc.TabsPanel(
                                plan_details_view_content, 
                                value="plans"
                                ),
                        ],
                        value="debt_details"
                    ), 
                    span={'base': 12, 'md': 3}),
                dmc.GridCol(
                    dmc.Tabs(
                        [
                            dmc.TabsList([
                                dmc.TabsTab("Graph View", value="graph_view"),
                                dmc.TabsTab("Table View", value="table_view"),
                            ]),
                            dmc.TabsPanel(
                                graph_view_content, 
                                value="graph_view"
                                ),
                            dmc.TabsPanel(
                                amortization_view_content, 
                                value="table_view"
                                ),
                        ],
                        value="graph_view"
                    ),
                    span={'base': 12, 'md': 9})
                ],
                gutter="xs"
            )
        ],
        size="xl",
        p="sm"),
    ],
    forceColorScheme='dark')

#################################################
###################### RUN ######################
#################################################

cb.register_callbacks(app)

def add_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.plot.ly https://fonts.googleapis.com https://api.iconify.design https://code.iconify.design; "
        "connect-src 'self' https://api.iconify.design https://api.simplesvg.com https://api.unisvg.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' data: https://fonts.gstatic.com https://fonts.googleapis.com; "
        "img-src 'self' data: https: https://api.iconify.design;"
    )
    return response

@app.server.after_request
def apply_security_headers(response):
    return add_security_headers(response)

if __name__ == '__main__':
    # Check if running in production
    is_production = (os.environ.get('GAE_ENV', '').startswith('standard') or 
                    os.environ.get('K_SERVICE') is not None)
    
    if is_production:
        app.run(
            debug=False, 
            port=int(os.environ.get('PORT', 8080)), 
            host='0.0.0.0'
        )
    else:
        app.run(debug=True, port=8050, host='127.0.0.1')