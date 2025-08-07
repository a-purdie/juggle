"""Main application layout definition."""

import dash_mantine_components as dmc
from dash import html
from source.content.disclaimers import get_disclaimer_content
from source.components.ui_components import (
    create_header_section,
    create_stores,
    create_debt_details_view_content,
    create_plan_details_view_content,
    create_graph_view_content,
    create_amortization_view_content
)


def create_disclaimer_drawer():
    """Create the disclaimer drawer component."""
    return dmc.Drawer(
        id="disclaimer_drawer",
        title="",
        size="md",
        position="right",
        opened=False,
        children=get_disclaimer_content()
    )


def create_main_tabs():
    """Create the main tab system for debt details and plans."""
    debt_details_view_content = create_debt_details_view_content()
    plan_details_view_content = create_plan_details_view_content()
    
    return dmc.GridCol(
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
        span={'base': 12, 'md': 3}
    )


def create_visualization_tabs():
    """Create the visualization tab system for graph and table views."""
    graph_view_content = create_graph_view_content()
    amortization_view_content = create_amortization_view_content()
    
    return dmc.GridCol(
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
        span={'base': 12, 'md': 9}
    )


def create_main_content():
    """Create the main content area with tabs."""
    main_tabs = create_main_tabs()
    visualization_tabs = create_visualization_tabs()
    
    return dmc.Grid([
        main_tabs,
        visualization_tabs
    ], gutter="xs")


def create_app_layout():
    """Create the complete application layout."""
    disclaimer_drawer = create_disclaimer_drawer()
    stores = create_stores()
    header_section = create_header_section()
    main_content = create_main_content()
    
    return dmc.MantineProvider([
        disclaimer_drawer,
        *stores,
        # Main app container
        dmc.Container([
            header_section,
            html.Hr(),
            main_content
        ],
        size="xl",
        p="sm"),
    ],
    forceColorScheme='dark')