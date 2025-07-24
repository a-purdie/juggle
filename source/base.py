import pandas as pd
import numpy as np
from amortization.schedule import amortization_schedule
from amortization.period import calculate_amortization_period
from amortization.amount import calculate_amortization_amount
from amortization.enums import PaymentFrequency
from typing import Iterator, Tuple
from datetime import datetime
from dateutil.relativedelta import relativedelta

class Frequencies:
    frequencies = {
        'Monthly': PaymentFrequency.MONTHLY,
        'monthly': PaymentFrequency.MONTHLY,
        'Fortnightly': PaymentFrequency.FORTNIGHTLY,
        'fortnightly': PaymentFrequency.FORTNIGHTLY,
        'Weekly': PaymentFrequency.WEEKLY,
        'weekly': PaymentFrequency.WEEKLY
    }

class Debt():
    """
    Base class for storing details about individual debts and producing an 
    individual debt's amortization schedule.
    """
    def __init__(self, name: str, account_type: str,
                 balance: float, interest_rate: float,
                 interest_calculation_method: str, payment_frequency: str,
                 next_payment_date: str, payment_amount: float):
        """
        Parameters
        ----------

        name: str
            A name for the debt; the name of the creditor is a good choice. If 
            there are multiple debts with the same creditor, give the debt a 
            separate name like 'Bank of America Auto Loan' and 'Bank of 
            America Mortgage'.

        accountType: {'personal', 'auto', 'mortgage', 'student', 'creditcard'}
            Specifies the type of debt.

        balance: float
            The actual balance of the debt as of the entry date.

        interestRate: float
            The annual interest rate charged on the debt. This rate is used to 
            create amortization schedules, and so it should not include any 
            fees like origination fees. In other words, this is not an APR, 
            only the rate at which interest accrues. Fees should be lumped in 
            with the `balance` parameter.

        interestCalculationMethod: {'simple', 'oneTwelvth'}
            The method used to compute the amount of interest charged in one 
            bill cycle. The 'simple' option refers to simple interest, i.e., 
            interest which accumulates on a daily basis as (1 / 365) * 
            principal.
            
        paymentFrequency: {'monthly', 'fortnightly', 'weekly'}
            The rate at which the paymentAmount is made. Most loans require a 
            payment monthly, but many people are paid every two weeks. In this 
            instance, you can save money by paying half the monthly payment 
            every two weeks.

        nextPaymentDate: str
            The next date a payment will be made on the debt. This is used 
            with `paymentFrequency` to determine the series of payment dates 
            all the way until it is paid off.     

        payment_amount: float
            The minimum payment due each payment period as specified by the 
            `payment_frequency` parameter. If you have to pay $300 per month on 
            a debt but want to make biweekly payments, then this amount should 
            be $150.    
        """
        self.name = name
        self.account_type = account_type
        self.balance = balance
        self.interest_rate = interest_rate
        self.interest_calculation_method = interest_calculation_method
        self.payment_frequency = payment_frequency
        self.next_payment_date = next_payment_date
        self.payment_amount = payment_amount

class Amortization():
    """
    Base class with methods for computing a debt's amortization schedule and 
    storing the schedule in a JSON file for future use.
    """
    def __init__(self, name: str, account_type: str,
                 balance: float, interest_rate: float,
                 interest_calculation_method: str, payment_frequency: str,
                 next_payment_date: str, payment_amount: float):
        
        self.debt = Debt(name, account_type, balance, interest_rate, 
                    interest_calculation_method, payment_frequency,
                    next_payment_date, payment_amount)
                    
    def schedule_by_amount(self) -> Iterator[Tuple[int, float, float, float, float]]:
        amortization_amount = self.debt.payment_amount
        frequency_string = self.debt.payment_frequency
        adjusted_interest = 0.01 * self.debt.interest_rate / \
            Frequencies.frequencies[frequency_string].value
        balance = self.debt.balance
        number = 0
        self.period = 0
        while balance > 0:
            number += 1
            self.period += 1
            interest = round(balance * adjusted_interest, 2)
            if amortization_amount < balance:
                principal = round(amortization_amount - interest, 2)
                balance = round(balance - principal, 2)
            else:
                principal, amortization_amount, balance = balance, \
                    balance + interest, 0
            yield number, amortization_amount, interest, principal, balance

    def get_payment_date_list(self):
        first_payment_date = datetime.strptime(
            self.debt.next_payment_date, '%Y-%m-%d')
        current_payment_date = first_payment_date
        date_list = [current_payment_date]
        if self.debt.payment_frequency == 'Weekly':
            one_week = relativedelta(weeks=1)
            for _ in range(self.period - 1):
                current_payment_date += one_week
                date_list.append(current_payment_date)
        elif self.debt.payment_frequency == 'Fortnightly':
            one_fortnight = relativedelta(weeks=2)
            for _ in range(self.period - 1):
                current_payment_date += one_fortnight
                date_list.append(current_payment_date)
        elif self.debt.payment_frequency == 'Monthly':
            one_month = relativedelta(months=1)
            if first_payment_date.day < 29:
                for _ in range(self.period - 1):
                    current_payment_date += one_month
                    date_list.append(current_payment_date)
            else:
                days_in_each_month = {
                    1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31,
                    9: 30, 10: 31, 11: 30, 12: 31}
                for _ in range(self.period - 1):
                    next_payment_date = current_payment_date + one_month
                    if next_payment_date.month is not None:  # Check for None
                        next_month_total_days = days_in_each_month[next_payment_date.month]
                        if next_month_total_days >= first_payment_date.day:
                            current_payment_date = datetime(
                                year=next_payment_date.year,
                                month=next_payment_date.month,
                                day=first_payment_date.day)
                        else:
                            current_payment_date = next_payment_date
                        date_list.append(current_payment_date)
        return [dates.strftime('%Y-%m-%d') for dates in date_list]

    def generate_amortization(self):
        schedule_object = self.schedule_by_amount()
        schedule_array = np.array([])
        for number, amount, interest, principal, balance in schedule_object:
            new_row = np.array([number, amount, interest, principal, balance])
            if len(schedule_array) > 0:
                schedule_array = np.vstack([schedule_array, new_row])
            else:
                schedule_array = new_row
        schedule_dataframe = pd.DataFrame(
            schedule_array, columns=[
                'Payment Date', 'Payment Amount', 'Interest', 
                'Principal', 'Balance Remaining'])
        schedule_dataframe['Payment Date'] = self.get_payment_date_list()
        self.amortization = schedule_dataframe
        pretty_schedule_dataframe = schedule_dataframe.__deepcopy__()
        for col in ['Payment Amount', 'Interest', 'Principal', 'Balance Remaining']:
            pretty_schedule_dataframe[col] = pretty_schedule_dataframe[col].map('${:,.2f}'.format)
        self.pretty_amortization = pretty_schedule_dataframe
        return self.amortization