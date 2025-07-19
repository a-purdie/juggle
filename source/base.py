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
    def __init__(self, name: str, accountType: str,
                 balance: float, interestRate: float,
                 interestCalculationMethod: str, paymentFrequency: str,
                 nextPaymentDate: str, paymentAmount: float):
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

        paymentAmount: float
            The minimum payment due each payment period as specified by the 
            `paymentFrequency` parameter. If you have to pay $300 per month on 
            a debt but want to make biweekly payments, then this amount should 
            be $150.    
        """
        self.name = name
        self.accountType = accountType
        self.balance = balance
        self.interestRate = interestRate
        self.interestCalculationMethod = interestCalculationMethod
        self.paymentFrequency = paymentFrequency
        self.nextPaymentDate = nextPaymentDate
        self.paymentAmount = paymentAmount

class Amortization():
    """
    Base class with methods for computing a debt's amortization schedule and 
    storing the schedule in a JSON file for future use.
    """
    def __init__(self, name: str, accountType: str,
                 balance: float, interestRate: float,
                 interestCalculationMethod: str, paymentFrequency: str,
                 nextPaymentDate: str, paymentAmount: float):
        
        self.debt = Debt(name, accountType, balance, interestRate, 
                    interestCalculationMethod, paymentFrequency, 
                    nextPaymentDate, paymentAmount)

    def scheduleByAmount(self) -> Iterator[Tuple[int, float, float, float, float]]:
        amortization_amount = self.debt.paymentAmount
        frequencyString = self.debt.paymentFrequency
        adjusted_interest = 0.01 * self.debt.interestRate / \
            Frequencies.frequencies[frequencyString].value
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

    def getPaymentDateList(self):
        firstPaymentDate = datetime.strptime(
            self.debt.nextPaymentDate, '%Y-%m-%d')
        currentPaymentDate = firstPaymentDate
        dateList = [currentPaymentDate]
        if self.debt.paymentFrequency == 'Weekly':
            oneWeek = relativedelta(weeks = 1)
            for _ in range(self.period - 1):
                currentPaymentDate += oneWeek
                dateList.append(currentPaymentDate)
        elif self.debt.paymentFrequency == 'Fortnightly':
            oneFortnight = relativedelta(weeks = 2)
            for _ in range(self.period - 1):
                currentPaymentDate += oneFortnight
                dateList.append(currentPaymentDate)
        elif self.debt.paymentFrequency == 'Monthly':
            oneMonth = relativedelta(months = 1)
            if firstPaymentDate.day < 29:
                for _ in range(self.period - 1):
                    currentPaymentDate += oneMonth
                    dateList.append(currentPaymentDate)
            else:
                daysInEachMonth = {
                    1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31,
                    9: 30, 10: 31, 11: 30, 12: 31}
                for _ in range(self.period - 1):
                    nextPaymentDate = currentPaymentDate + oneMonth
                    nextMonthTotalDays = daysInEachMonth[nextPaymentDate.month]
                    if nextMonthTotalDays >= firstPaymentDate.day:
                        currentPaymentDate = datetime(
                            year = nextPaymentDate.year,
                            month = nextPaymentDate.month,
                            day = firstPaymentDate.day)
                    else:
                        currentPaymentDate = nextPaymentDate
                    dateList.append(currentPaymentDate)
        return [dates.strftime('%Y-%m-%d') for dates in dateList]

    def getAmortization(self):
        scheduleObject = self.scheduleByAmount()
        scheduleArray = np.array([])
        for number, amount, interest, principal, balance in scheduleObject:
            newRow = np.array([number, amount, interest, principal, balance])
            if len(scheduleArray) > 0:
                scheduleArray = np.vstack([scheduleArray, newRow])
            else:
                scheduleArray = newRow
        scheduleDataFrame = pd.DataFrame(
            scheduleArray, columns = [
                'Payment Date', 'Payment Amount', 'Interest', 
                'Principal', 'Balance Remaining'])
        scheduleDataFrame['Payment Date'] = self.getPaymentDateList()
        self.amortization = scheduleDataFrame
        prettyScheduleDataFrame = scheduleDataFrame.__deepcopy__()
        for col in ['Payment Amount', 'Interest', 'Principal', 'Balance Remaining']:
            prettyScheduleDataFrame[col] = prettyScheduleDataFrame[col].map('${:,.2f}'.format)
        self.prettyAmortization = prettyScheduleDataFrame
        return self.amortization