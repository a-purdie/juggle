import dash_bootstrap_components as dbc
from datetime import datetime
import base as b
import dash_mantine_components as dmc

def getAmortization(
        name, accountType, balance, interestRate, 
        interestCalculationMethod, paymentFrequency, nextPaymentDate, 
        paymentAmount):
    amort = b.Amortization(
        name, accountType, balance, interestRate, 
        interestCalculationMethod, paymentFrequency, 
        nextPaymentDate, paymentAmount)
    amort.getAmortization()
    return amort

def checkDebtIndex(fieldName, debtIndex):
    if debtIndex is None:
        id = fieldName
    else:
        id = {
            'type': f'edit{fieldName[0].upper()}{fieldName[1:]}Input',
            'index': debtIndex
            }
    return id

def createDebtNameInput(debtIndex = None, value = None):
    id = checkDebtIndex('name', debtIndex)

    nameInput = dbc.Row([
    dbc.Label(
        "Name", 
        html_for = id, 
        width = 5, 
        style = {'font-size': 16}),
    dbc.Col(dbc.Input(
            id = id,
            value = value), 
            width = 7)], 
        className = 'mb-1') 
    
    return nameInput

def createBalanceInput(debtIndex = None, value = None):
    id = checkDebtIndex('balance', debtIndex)

    balanceInput = dbc.Row([
        dbc.Label(
            "Balance", 
            html_for = id, 
            width = 5, 
            style = {'font-size': 16}),
        dbc.Col(dbc.InputGroup([
            dbc.InputGroupText("$"), 
            dbc.Input(id = id, value = value),
            dbc.FormFeedback(
                'The payment amount exceeds the balance.', type = 'invalid'
            )]), width = 7)], className = 'mb-1')
    
    return balanceInput

def createInterestRateInput(debtIndex = None, value = None):
    id = checkDebtIndex('interestRate', debtIndex)

    interestRateInput = dbc.Row([
    dbc.Label(
        "Interest Rate", 
        html_for = id, 
        width = 5, 
        style = {'font-size': 16}),
    dbc.Col(dbc.InputGroup([
        dbc.Input(id = id, value = value,), 
        dbc.InputGroupText('%')]), width = 7)], className = 'mb-1')

    return interestRateInput

def createPaymentAmountInput(debtIndex = None, value = None):
    id = checkDebtIndex('paymentAmount', debtIndex)

    paymentAmountInput = dbc.Row([
        dbc.Label(
            "Payment Amount", 
            html_for = id, 
            width = 5, 
            style = {'font-size': 16}),
        dbc.Col(dbc.InputGroup([
            dbc.InputGroupText("$"), 
            dbc.Input(id = id, value = value,),
            dbc.FormFeedback(
                ('This payment amount does not cover the amount of interest '
                'that accrues each bill cycle'), 
                type = 'invalid')]), width = 7)], className = 'mb-1')
    
    return paymentAmountInput

def createPaymentFrequencyInput(debtIndex = None, value = None):
    id = checkDebtIndex('paymentFrequency', debtIndex)
    
    paymentFrequencyInput = dbc.Row([
        dbc.Label(
            "Frequency", 
            html_for = id, 
            width = 5, 
            style = {'font-size': 16}),
        dbc.Col(dbc.Select(
            id = id, value = value,
            options = [{"label": "Monthly", "value": "Monthly"},
                        {"label": "Fortnightly", "value": "Fortnightly"},
                        {"label": "Weekly", "value": "Weekly"}]), 
            width = 7)], className = 'mb-1')

    return paymentFrequencyInput

def createNextPaymentDateInput(debtIndex = None, value = None):
    id = checkDebtIndex('nextPaymentDate', debtIndex)

    nextPaymentDateInput = dbc.Row([
    dbc.Label(
        "Next Payment", 
        html_for = id, 
        width = 5, 
        style = {'font-size': 16}),
    dbc.Col(dmc.DatePickerInput(
        id = id, value = value,
        minDate = datetime.today(),
        valueFormat = 'YYYY-MM-DD'), width = 7)], className = 'mb-1')
    
    return nextPaymentDateInput

def createAddOrEditDebtButton(debtIndex = None):
    if debtIndex is None:
        id = 'addDebtButton'
        buttonText = "Add Debt"
    else:
        id = {'type': 'editDebtButton', 'index': debtIndex}
        buttonText = "Edit Debt"

    debtButton = dbc.Row([
        dbc.Button(
            buttonText, 
            id = id, 
            n_clicks = 0, 
            disabled = True)],
        className = 'col-8 mx-auto')
    
    return debtButton

def lightenHexColor(hexCode, amount=0.5):
    """
    From a hex code, convert to RGB, blend with white, and return the 
    lightened color's hex code.
    """
    hexCode = hexCode.lstrip('#')
    r = int(hexCode[0:2], 16)
    g = int(hexCode[2:4], 16)
    b = int(hexCode[4:6], 16)

    r = int(r + (255 - r) * amount)
    g = int(g + (255 - g) * amount)
    b = int(b + (255 - b) * amount)

    return '#{:02x}{:02x}{:02x}'.format(r, g, b)