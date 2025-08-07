"""Disclaimer and privacy policy content for the application."""

import dash_mantine_components as dmc
from dash import html


def get_disclaimer_content():
    """Returns the disclaimer and privacy policy content for the drawer."""
    return [
        dmc.Title("Disclaimer", order=1), 
        html.Hr(),
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
        ), 
        html.Hr(),
        dmc.Title("Privacy Policy", order=1),
        dmc.Text(
            "Last updated: August 6, 2025", size="xs"
        ),
        html.Hr(),
        dmc.Title("Overview", order=2),
        dmc.Text(
            "This privacy policy explains how your personal and financial "
            "information is handled when you use this debt management application "
            """("the App"). I take your privacy seriously, and you """
            "deserve transparency about my app's data practices.", size="xs"
        ), 
        html.Br(),
        dmc.Title("What Information We Collect", order=2),
        dmc.Text(
            "When you use the App, it processes the following information that "
            "you voluntarily provide:", size="xs"
        ),
        dmc.List([
            dmc.ListItem(dmc.Text(
                "Financial Data: Debt balances, interest rates, payment amounts, "
                "payment frequencies, and payment dates", size="xs")),
            dmc.ListItem(dmc.Text(
                "Account Names: Labels you assign to your debts for organization "
                "purposes", size="xs")),
            dmc.ListItem(dmc.Text(
                "Usage Data: Technical information about how you interact with "
                "the App", size="xs"))
        ], size="xs"),
        html.Br(),
        dmc.Title("How We Process Your Information", order=2),
        dmc.Title("Server-Side Processing", order=4),
        dmc.Text(
            "This App is hosted on Google Cloud Platform. When you add or edit "
            "debt information, generate amortization schedules, view payment "
            "projections and graphs, or perform calculations, your data is "
            "temporarily sent to and processed on Google's servers.", size="xs"
        ),
        dmc.Text("This server-side processing is necessary to:", size="xs"),
        dmc.List([
            dmc.ListItem(dmc.Text(
                "Perform complex financial calculations", size="xs")),
            dmc.ListItem(dmc.Text(
                "Generate amortization tables and payment schedules", size="xs")),
            dmc.ListItem(dmc.Text(
                "Create visualizations and graphs", size="xs")),
            dmc.ListItem(dmc.Text(
                "Provide real-time updates to your debt management dashboard", 
                size="xs"))
        ], size="xs"),
        html.Br(),
        dmc.Title("Temporary Storage", order=4),
        dmc.List([
            dmc.ListItem(dmc.Text(
                "Your financial data is stored temporarily in your browser's "
                "memory while you use the App", size="xs")),
            dmc.ListItem(dmc.Text(
                "Data is transmitted to our servers only when performing "
                "calculations or updates", size="xs")),
            dmc.ListItem(dmc.Text(
                "We do not permanently store your financial information in "
                "databases", size="xs")),
            dmc.ListItem(dmc.Text(
                "Your session data is cleared when you close your browser", 
                size="xs"))
        ], size="xs"),
        html.Br(),
        dmc.Title("Data Sharing and Third Parties", order=2),
        dmc.Title("Google Cloud Platform", order=4),
        dmc.Text(
            "As the App's hosting provider, Google Cloud Platform may have access to "
            "your data during processing. Google's own privacy policies and "
            "security measures apply to this processing.", size="xs"
        ),
        html.Br(),
        dmc.Title("No Data Sales or Marketing", order=4),
        dmc.Text("This App does not:", size="xs"),
        dmc.List([
            dmc.ListItem(dmc.Text(
                "Sell your personal or financial information to third parties", 
                size="xs")),
            dmc.ListItem(dmc.Text(
                "Use your data for marketing purposes", size="xs")),
            dmc.ListItem(dmc.Text(
                "Share your information with advertisers", size="xs")),
            dmc.ListItem(dmc.Text(
                "Create profiles for commercial purposes", size="xs"))
        ], size="xs"),
        html.Br(),
        dmc.Title("Data Security", order=2),
        dmc.Text("I implement security measures including:", size="xs"),
        dmc.List([
            dmc.ListItem(dmc.Text(
                "Encrypted data transmission (HTTPS)", size="xs")),
            dmc.ListItem(dmc.Text(
                "Secure hosting infrastructure through Google Cloud Platform", 
                size="xs")),
            dmc.ListItem(dmc.Text(
                "No permanent storage of sensitive financial data", size="xs")),
            dmc.ListItem(dmc.Text(
                "Session-based data handling", size="xs"))
        ], size="xs"),
        dmc.Text(
            "However, no method of transmission over the internet is 100% secure. "
            "While I strive to protect your information, I cannot guarantee "
            "absolute security.", size="xs"
        ),
        html.Br(),
        dmc.Title("Your Data Rights", order=2),
        dmc.Text("You have the right to:", size="xs"),
        dmc.List([
            dmc.ListItem(dmc.Text(
                "Access: Review what information is being processed", size="xs")),
            dmc.ListItem(dmc.Text(
                "Control: Decide what financial information to input", size="xs")),
            dmc.ListItem(dmc.Text(
                "Delete: Clear your session data by closing your browser", 
                size="xs")),
            dmc.ListItem(dmc.Text(
                "Withdraw: Stop using the App at any time", size="xs"))
        ], size="xs"),
        html.Br(),
        dmc.Title("Data Retention", order=2),
        dmc.List([
            dmc.ListItem(dmc.Text(
                "Financial data is only retained during your active browser "
                "session", size="xs")),
            dmc.ListItem(dmc.Text(
                "No permanent copies of your financial information are stored", 
                size="xs")),
            dmc.ListItem(dmc.Text(
                "Session data is automatically cleared when you close the App", 
                size="xs"))
        ], size="xs"),
        html.Br(),
        dmc.Title("International Data Processing", order=2),
        dmc.Text(
            "Your information may be processed on servers located outside your "
            "country of residence, including in the United States where Google "
            "Cloud Platform operates data centers.", size="xs"
        ),
        html.Br(),
        dmc.Title("Changes to This Policy", order=2),
        dmc.Text(
            "This privacy policy may change periodically. Any changes "
            "will be posted on this page with an updated 'Last updated' date.", 
            size="xs"
        ),
        html.Hr()
    ]