# `juggle`
This is a Dash app that allows you to plan how you're going to pay off all of your debt. 

It's currently deployed at [indentured.services](https://indentured-services) using a Google Cloud Platform (GCP) Cloud Run instance with a trigger that pushes live updates to the app whenever commits are merged into this repository's main branch..

You can enter the details of each of your accounts and `juggle` will create an elegant visualization of your payoff timeline and an amortization schedule.

My motivation for building this app was not just to get more experience writing Dash apps, but was also to get experience deploying applications using Google Cloud Platform (GCP).

## Disclaimer

This application does not provide financial advice. The payoff graphs, amortization tables, and financial projections provided by `juggle` are for informational purposes only. The projections are only estimates based on the information you provide and standard financial formulas. They are not guarantees of when or how your debt will be paid off.

Your actual results will vary due to changes in interest rates, payment schedules, additional fees assessed by lenders, or other factors outside of this application's calculations. Financial decisions should not be made solely on the basis of these projections.