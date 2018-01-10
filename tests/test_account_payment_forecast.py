# This file is part of the account_payment_forecast module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class AccountPaymentForecastTestCase(ModuleTestCase):
    'Test Account Payment Forecast module'
    module = 'account_payment_forecast'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        AccountPaymentForecastTestCase))
    return suite
