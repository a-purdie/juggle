import plotly.express.colors as color

# The color_order determines the order of colors used in the payoff graph and 
# amortization cards as debts are added
color_order = color.qualitative.Dark24

# Payment frequency definitions
PAYMENT_FREQUENCY_DAYS = {'Monthly': 31, 'Fortnightly': 14, 'Weekly': 7}

# Interest rate calculation constants
DAYS_IN_YEAR_FOR_PERCENTAGE = 36500  # 365 * 100 for percentage calculation

# UI constants
FORMATTING_DIVISOR = 1000  # Division factor for formatting (e.g., thousands)
SCROLL_DELAY_MS = 200  # Timeout delay in milliseconds for auto-scroll