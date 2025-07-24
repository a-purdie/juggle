from dash import html, dcc
from dash.dependencies import Input, Output, State, MATCH
from dash_iconify import DashIconify
import dash_mantine_components as dmc
from utils import helpers as h
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from utils import constants as c
import base as b


#################################################
################### CALLBACKS ###################
#################################################

def register_callbacks(app):
    @app.callback(
        Output('paymentAmount', 'invalid'),
        Output('balance', 'invalid'),
        Output('addDebtButton', 'disabled', allow_duplicate = True),
        Output('addDebtButton', 'active'),
        Input('name', 'value'),
        Input('balance', 'value'),
        Input('interestRate', 'value'),
        Input('paymentAmount', 'value'),
        Input('paymentFrequency', 'value'),
        Input('nextPaymentDate', 'value'),
        prevent_initial_call = True
    )
    def checkAddDebtFormForRequiredFields(
        name, balance, interestRate, paymentAmount, paymentFrequency, 
        nextPaymentDate):
        """
        Makes sure that the Add Debt button is only enabled when each field is 
        filled with valid values. Add Debt button is disabled by this callback 
        if the amount of interest that accrues in a pay period exceeds the 
        provided payment amount. Add Debt button is disabled if any of the six 
        fields are blank. Add Debt button is disabled if the payment amount 
        exceeds the balance.
        """
        paymentAmountArgs = [
            balance, interestRate, paymentAmount, paymentFrequency
        ]
        if all(i is not None and len(i) > 0 for i in paymentAmountArgs):
            # If the user has entered a balance, rate, payment amount, and 
            # payment frequency...
            days = {'Monthly': 31, 'Fortnightly': 14, 'Weekly': 7}
            periodInterest = (
                float(balance) 
                * float(interestRate) 
                * (days[paymentFrequency]/36500)
            )
            if periodInterest > float(paymentAmount):
                # And if the payment amount won't cover the interest amount 
                # that accrues based on the selected frequency, disable the 
                # add debt button and display the Payment Amount invalid 
                # feedback.
                return True, False, True, False
            if float(balance) < float(paymentAmount):
                return False, True, True, False
        else:
            # If the user has not entered a balance, rate, payment amount, or 
            # payment frequency yet, then disable the add debt button.
            return False, False, True, False
        args = [name, balance, interestRate, paymentAmount, 
            paymentFrequency, nextPaymentDate]
        if all(i is not None for i in args):
            # If the user has filled in all the fields properly, enable the add 
            # debt button.
            return False, False, False, True
        else:
            # If the user has not filled in all the fields with valid entries, 
            # disable the add debt button.
            return False, False, True, False

    @app.callback(
        Output({'type': 'editPaymentAmountInput', 'index': MATCH}, 'invalid'),
        Output({'type': 'editBalanceInput', 'index': MATCH}, 'invalid'),
        Output(
            {'type': 'editDebtButton', 'index': MATCH}, 
            'disabled', 
            allow_duplicate = True),
        Output({'type': 'editDebtButton', 'index': MATCH}, 'active'),
        Input({'type': 'editNameInput', 'index': MATCH}, 'value'),
        Input({'type': 'editBalanceInput', 'index': MATCH}, 'value'),
        Input({'type': 'editInterestRateInput', 'index': MATCH}, 'value'),
        Input({'type': 'editPaymentAmountInput', 'index': MATCH}, 'value'),
        Input({'type': 'editPaymentFrequencyInput', 'index': MATCH}, 'value'),
        Input({'type': 'editNextPaymentDateInput', 'index': MATCH}, 'value'),
        prevent_initial_call = True
    )
    def checkEditDebtFormForRequiredFields(
        name, balance, interestRate, paymentAmount, paymentFrequency, 
        nextPaymentDate):
        """
        Makes sure that the Add Debt button is only enabled when each field is 
        filled with valid values. Add Debt button is disabled by this callback 
        if the amount of interest that accrues in a pay period exceeds the 
        provided payment amount. Add Debt button is disabled if any of the 
        six fields are blank. Add Debt button is disabled if the payment 
        amount exceeds the balance.
        """
        paymentAmountArgs = [
            balance, interestRate, paymentAmount, paymentFrequency
        ]
        if all(i is not None and len(i) > 0 for i in paymentAmountArgs):
            # If the user has entered a balance, rate, payment amount, and 
            # payment frequency...
            days = {'Monthly': 31, 'Fortnightly': 14, 'Weekly': 7}
            periodInterest = (
                float(balance) 
                * float(interestRate) 
                * (days[paymentFrequency]/36500)
            )
            if periodInterest > float(paymentAmount):
                # And if the payment amount won't cover the interest amount 
                # that accrues based on the selected frequency, disable the 
                # add debt button and display the Payment Amount invalid 
                # feedback.
                return True, False, True, False
            if float(balance) < float(paymentAmount):
                return False, True, True, False
        else:
            # If the user has not entered a balance, rate, payment amount, or 
            # payment frequency yet, then disable the add debt button.
            return False, False, True, False
        args = [name, balance, interestRate, paymentAmount, 
            paymentFrequency, nextPaymentDate]
        if all(i is not None for i in args):
            # If the user has filled in all the fields properly, enable the 
            # add debt button.
            return False, False, False, True
        else:
            # If the user has not filled in all the fields with valid entries, 
            # disable the add debt button.
            return False, False, True, False

    @app.callback(
        Output('addDebtFormCollapse', 'opened'),
        Input('openAddDebtFormButton', "n_clicks"),
        State('addDebtFormCollapse', 'opened'),
        prevent_initial_call = True
    )
    def toggleAddDebtForm(n_clicks, is_open):
        if is_open:
            return False
        else:
            return True

    @app.callback(
        Output({'type': 'editDebtCollapse', 'index': MATCH}, 'opened'),
        Input({'type': 'openEditDebtFormButton', 'index': MATCH}, 'n_clicks'),
        State({'type': 'editDebtCollapse', 'index': MATCH}, 'opened'),
        prevent_initial_call = True
    )
    def toggleEditDebtForm(n_clicks, is_open):
        if is_open:
            return False
        else:
            return True

    @app.callback(
        Output('makePlanFormCollapse', 'opened'),
        Input('openMakePlanFormButton', "n_clicks"),
        State('makePlanFormCollapse', 'opened'),
        prevent_initial_call = True
    )
    def toggleMakePlanForm(n_clicks, is_open):
        if is_open:
            return False
        else:
            return True

    @app.callback(
            Output('payoffGraph', 'figure'),
            Output('amortizations-store', 'data'),
            Output('debt-details-store', 'data'),
            Output('amortizationSchedule', 'children'),
            Output('debtCardsContainer', 'children'),
            Output('addDebtButton', 'disabled', allow_duplicate=True),
            Output('addDebtButton', 'n_clicks'),
            Output('name', 'value'),
            Output('balance', 'value'),
            Output('interestRate', 'value'),
            Output('paymentAmount', 'value'),
            Output('paymentFrequency', 'value'),
            Output('nextPaymentDate', 'value'),
            [
                State('amortizations-store', 'data'),
                State('debt-details-store', 'data'),
                State('name', 'value'),
                State('balance', 'value'),
                State('interestRate', 'value'),
                State('paymentAmount', 'value'),
                State('paymentFrequency', 'value'),
                State('nextPaymentDate', 'value'),
                State('payoffGraph', 'figure'),
                Input('addDebtButton', 'n_clicks')
            ],
            prevent_initial_call=True,
    )
    def makeGraphAndAmortizationTable(
        amortizations_data, debt_details_data, name, balance, rate, 
        paymentAmount, frequency, nextPaymentDate, figDict, n_clicks):
        """
        Creates the debt graph and table views.
        """
        # Initialize store data if None
        if amortizations_data is None:
            amortizations_data = []
        if debt_details_data is None:
            debt_details_data = {}

        currentDebtIndex = n_clicks - 1

        debtColor = c.colorOrder[currentDebtIndex % len(c.colorOrder)]
        lighterDebtColor = h.lightenHexColor(debtColor, amount=0.5)

        amortObject = b.Amortization(
            name=name, accountType='personal', balance=float(balance), 
            interestRate=float(rate), interestCalculationMethod='simple', 
            paymentFrequency=frequency, nextPaymentDate=nextPaymentDate, 
            paymentAmount=float(paymentAmount)
        )
        amortObject.getAmortization()

        x = list(amortObject.amortization['Payment Date'])
        y = list(amortObject.amortization['Balance Remaining'])
        traces = {'x': x, 'y': y}

        amortizationCard = html.Div([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row(html.H3(name, className='card_title')),
                    dbc.Row(
                        dbc.Table([
                            html.Thead([
                                html.Tr([html.Th(col) for col in amortObject.prettyAmortization.columns])
                            ]),
                            html.Tbody([
                                html.Tr([
                                    html.Td(amortObject.prettyAmortization.iloc[i][col]) 
                                    for col in amortObject.prettyAmortization.columns
                                ]) for i in range(len(amortObject.prettyAmortization))
                            ])
                        ], striped=True, bordered=True, hover=True, style={'width': '100vw'})
                    )
                ])
                ], color=debtColor),
            html.Hr()],
            id={'type': 'amortizationCards', 'index': currentDebtIndex})
        
        # Add to amortizations store data
        updated_amortizations = amortizations_data.copy()
        updated_amortizations.append(amortizationCard)

        editDebtControls = dbc.Card([
        dbc.CardBody([
            html.H3("Edit Debt", className = 'card_title'),
            html.P("All fields are required.", style = {'fontSize': 14}),
            dbc.Form([
                h.createDebtNameInput(currentDebtIndex, name), 
                h.createBalanceInput(currentDebtIndex, balance),
                h.createInterestRateInput(currentDebtIndex, rate), 
                h.createPaymentAmountInput(currentDebtIndex, paymentAmount),
                h.createPaymentFrequencyInput(currentDebtIndex, frequency), 
                h.createNextPaymentDateInput(currentDebtIndex, nextPaymentDate)
                ]),
            html.Hr(),
            h.createAddOrEditDebtButton(currentDebtIndex)])])

        debtDetailsCard = html.Div([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(html.H4(
                            name, 
                            className = 'card_title'), width = 10),
                        dbc.Col(
                            dmc.ActionIcon(
                                DashIconify(icon = 'iconoir:edit', width = 30),
                                size = 'lg',
                                n_clicks = 0,
                                color = lighterDebtColor,
                                variant = 'subtle', 
                                id = {
                                    'type': 'openEditDebtFormButton', 
                                    'index': currentDebtIndex
                                    }),
                            width = 2)
                        ]), 
                    dbc.Row([
                        dbc.Col(f"Balance: ${float(balance):,.2f}"), 
                        dbc.Col(f"Rate: {float(rate):,.2f}%")], 
                        style = {'font-size': 12}),
                    dbc.Row([
                        dbc.Col(f"Payment Amount: ${float(paymentAmount):,.2f}"), 
                        dbc.Col(f"{frequency} Payments")],
                        style = {'font-size': 12}),
                    dbc.Row(
                        dbc.Col(f"Next Payment Date: {nextPaymentDate}"),
                        style = {'font-size': 12})
                    ])], 
                color = debtColor),
            html.Hr(),
            dmc.Drawer(
                editDebtControls, 
                id = {'type': 'editDebtCollapse', 'index': currentDebtIndex},
                opened = False
            )], 
            id={'type': 'debtCards', 'index': currentDebtIndex})
        
        # Add to debt details store data
        updated_debt_details = debt_details_data.copy()
        updated_debt_details[currentDebtIndex] = {
            'name': name,
            'balance': balance,
            'rate': rate,
            'paymentAmount': paymentAmount,
            'frequency': frequency,
            'nextPaymentDate': nextPaymentDate,
            'traces': traces,
            'color': debtColor,
            'card': debtDetailsCard
        }

        fig = go.Figure(figDict)

        fig.add_trace(go.Scatter(
            x=x, 
            y=y,
            line={'color': debtColor},
            name=str(currentDebtIndex)))

        fig.update_layout(showlegend=False)

        # Create list of debt detail cards from the store data
        debt_detail_cards = []
        for debt_index, debt_data in updated_debt_details.items():
            if 'card' in debt_data:
                debt_detail_cards.append(debt_data['card'])

        return (fig, updated_amortizations, updated_debt_details, 
                updated_amortizations, debt_detail_cards, True, n_clicks, 
                '', '', '', '', '', None)