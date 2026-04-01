
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from datetime import date
from decimal import Decimal

from trytond.modules.account.tests import create_chart, get_fiscalyear
from trytond.modules.company.tests import (
    CompanyTestMixin, create_company, set_company)
from trytond.pool import Pool
from trytond.tests.test_tryton import ModuleTestCase, with_transaction


class AccountPaymentForecastTestCase(CompanyTestMixin, ModuleTestCase):
    'Test AccountPaymentForecast module'
    module = 'account_payment_forecast'

    @with_transaction()
    def test_report_execute(self):
        pool = Pool()
        Account = pool.get('account.account')
        FiscalYear = pool.get('account.fiscalyear')
        Journal = pool.get('account.journal')
        Move = pool.get('account.move')
        Party = pool.get('party.party')
        PaymentType = pool.get('account.payment.type')
        Report = pool.get('account_payment_forecast.forecast', type='report')

        company = create_company()
        with set_company(company):
            create_chart(company)
            fiscalyear = get_fiscalyear(company)
            fiscalyear.save()
            FiscalYear.create_period([fiscalyear])
            period = fiscalyear.periods[0]

            journal_revenue, = Journal.search([
                    ('code', '=', 'REV'),
                    ], limit=1)
            revenue, = Account.search([
                    ('type.revenue', '=', True),
                    ('closed', '=', False),
                    ('company', '=', company.id),
                    ], limit=1)
            receivable, = Account.search([
                    ('type.receivable', '=', True),
                    ('closed', '=', False),
                    ('company', '=', company.id),
                    ], limit=1)
            party, = Party.create([{
                        'name': 'Customer',
                        }])
            payment_type, = PaymentType.create([{
                        'name': 'Transfer',
                        'kind': 'receivable',
                        'company': company.id,
                        }])

            moves = Move.create([{
                        'period': period.id,
                        'journal': journal_revenue.id,
                        'date': period.start_date,
                        'lines': [('create', [{
                                        'account': revenue.id,
                                        'credit': Decimal('100.00'),
                                        }, {
                                        'party': party.id,
                                        'account': receivable.id,
                                        'debit': Decimal('100.00'),
                                        'payment_type': payment_type.id,
                                        'maturity_date': date(
                                            period.start_date.year, 4, 30),
                                        }])],
                        }, {
                        'period': period.id,
                        'journal': journal_revenue.id,
                        'date': period.start_date,
                        'lines': [('create', [{
                                        'account': revenue.id,
                                        'credit': Decimal('50.00'),
                                        }, {
                                        'party': party.id,
                                        'account': receivable.id,
                                        'debit': Decimal('50.00'),
                                        'payment_type': payment_type.id,
                                        'maturity_date': date(
                                            period.start_date.year, 6, 29),
                                        }])],
                        }])

            lines = [line.id for move in moves for line in move.lines
                if line.account == receivable]
            ext, content, _, _ = Report.execute(lines, {})
            self.assertEqual(ext, 'pdf')
            self.assertTrue(content)


del ModuleTestCase
