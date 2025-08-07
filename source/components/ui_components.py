"""Reusable UI components for the debt management application."""

import dash_mantine_components as dmc
from dash import html, dcc
import plotly.graph_objects as go
import pandas as pd
from source.utils.helpers import create_plans_coming_soon
from dash_iconify import DashIconify


def create_plan_form_components():
    """Create plan form components."""
    
    # Plan name input
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

    # Info icon for plan type hover card
    info_icon = html.I(
        className='fa-solid fa-circle-info', 
        style={'color': '#aaaaaa'})

    # Plan type information for hover card
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

    # Plan type radio with hover card
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

    # Add plan button
    add_plan_button = dmc.Grid([
        dmc.GridCol(
            dmc.Button("Add Plan", id='add_plan', n_clicks=0, disabled=True),
            span=8,
            offset=2
        )])

    return plan_name_input, plan_type_radio, add_plan_button


def create_add_plan_controls():
    """Create the complete add plan controls card."""
    plan_name_input, plan_type_radio, add_plan_button = create_plan_form_components()
    
    return dmc.Card([
        dmc.CardSection([
            html.H3("Make a Plan", className='card_title'),
            dmc.Stack([plan_name_input, plan_type_radio]),
            html.Hr(),
            add_plan_button
        ], p="md")
    ])


def create_graph_view_content():
    """Create the graph view content."""
    return dmc.GridCol(dcc.Graph(
            figure=go.Figure(
                data=go.Scatter(), 
                layout=go.Layout(
                    template='plotly_dark',
                    yaxis_tickprefix='$', 
                    yaxis_tickformat=',.2f',
                    margin=dict(l=40, r=40, t=60, b=40)  # Reduce margins for more space
                )),
            id='payoff_graph', 
            style={'width': '100%', 'height': 'calc(95vh - 150px)'},  # Dynamic height based on viewport
            config={'responsive': True, 'displayModeBar': False}), 
        )


def create_amortization_view_content():
    """Create the amortization table view content."""
    return dmc.GridCol([], id='amortization_schedule', span=12)


def create_debt_form_drawer():
    """Create the debt form drawer component."""
    return dmc.Drawer(
        id='debt_form_drawer',
        title="",
        opened=False,
        children=[]
    )


def create_debt_cards_container():
    """Create the debt cards container with scrolling."""
    return html.Div(
        [], 
        id='debt_cards_container',
        className='debt-cards-container',
        style={
            'maxHeight': 'calc(95vh - 180px)',
            'overflowY': 'auto',  # Show scrollbar only when its needed
            'scrollbarWidth': 'thin',  # Thinner scrollbar for Firefox users
            'msOverflowStyle': 'none',  # Hide scrollbar in Edge
        }
    )


def create_debt_details_view_content():
    """Create the main debt details view with add button and cards container."""
    debt_cards_container = create_debt_cards_container()
    debt_form_drawer = create_debt_form_drawer()
    
    return dmc.GridCol([
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


def create_plan_details_view_content():
    """Create the plan details view content."""
    return dmc.GridCol(
        create_plans_coming_soon(), id='plan_details_view', span=12)


def create_header_section():
    """Create the application header section."""
    return dmc.Grid([
        dmc.GridCol([
            html.H1("indentured.services", style={'font-family': 'Chonburi'}),
            html.P(
                "Break the chains of your peonage and claim delicious freedom at last",
                style={'fontSize': 10}),
        ], span={'base': 8, 'md': 10}),
        dmc.GridCol([
            dmc.Group([
                dmc.Button(
                    "Legal",
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
    ])


def create_stores():
    """Create the dcc.Store components for state management."""
    return [
        dcc.Store(id='amortizations-store', data=[]),
        dcc.Store(id='debt-details-store', data={}),
        dcc.Store(id='form-state-store', data={'mode': 'add', 'debt_index': None}),
        html.Div(id='scroll-trigger', style={'display': 'none'}),  # Dummy div for clientside callback
    ]