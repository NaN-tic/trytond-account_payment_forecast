# This file is part account_payment_forecast module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from datetime import date, datetime
from decimal import Decimal
from itertools import groupby

from dominate.tags import div, h1, header as header_tag, span, table
from dominate.tags import tbody, td
from dominate.tags import tfoot, th, thead, tr

from trytond.pool import PoolMeta
from trytond.transaction import Transaction
from trytond.tools import file_open
from trytond.modules.html_report.dominate_report import DominateReport
from trytond.modules.html_report.engine import render as html_render
from trytond.modules.html_report.i18n import _


_ZERO = Decimal('0.0')


class ForecastReport(DominateReport, metaclass=PoolMeta):
    __name__ = 'account_payment_forecast.forecast'
    side_margin = 1
    _single = False

    @classmethod
    def language(cls, records):
        return Transaction().language or 'en'

    @classmethod
    def css(cls, action, data, records):
        now = datetime.now().strftime('%d/%m/%Y %H:%M')
        with file_open('account_payment_forecast/forecast.css') as css_file:
            css = css_file.read()
        return '%s\n%s' % (
            css,
            ('@page {'
             '@bottom-left {'
             'content: "%s";'
             "font-family: 'Arial';"
             'font-size: 9px;'
             'padding-bottom: 0.5cm;'
             '}'
             '}') % now)

    @classmethod
    def show_company_info(cls, company, show_party=True,
            show_contact_mechanism=True):
        container = div(id='company-info', cls='header-details')
        container.add(span(company.party.render.name, cls='company-info-name'))
        return container

    @classmethod
    def show_document_info(cls, record):
        container = div(cls='forecast-document-info')
        container.add(h1(_('Payment/receivables forecast'), cls='document'))
        return container

    @classmethod
    def header(cls, action, data, records):
        record = records[0]
        header = div()
        company = record.company
        document_info = cls.show_document_info(record)
        header_box = div(cls='forecast-header')
        header_box.add(div(
                cls.show_company_info(company),
                cls='forecast-header-company'))
        header_box.add(div(
                document_info,
                cls='forecast-header-document text-right'))
        header_node = header_tag(id='header')
        header_node.add(header_box)
        header.add(header_node)
        return header

    @classmethod
    def footer(cls, action, data, records):
        pass

    @classmethod
    def title(cls, action, data, records):
        return _('Payment/receivables forecast')

    @classmethod
    def _amount(cls, record):
        debit = record.raw.debit or _ZERO
        credit = record.raw.credit or _ZERO
        return debit - credit

    @classmethod
    def _bank_account_number(cls, record):
        return (record.bank_account and record.bank_account.numbers
            and record.bank_account.numbers[0].render.number or '')

    @classmethod
    def _bank_name(cls, record):
        return (record.bank_account and record.bank_account.bank
            and record.bank_account.bank.party
            and record.bank_account.bank.party.render.name or '')

    @classmethod
    def _document(cls, record):
        move_origin = record.move_origin
        if not move_origin:
            return ''
        if hasattr(move_origin.raw, 'number'):
            return (move_origin.raw.number and move_origin.render.number or '')
        return move_origin.render.rec_name

    @classmethod
    def _origin(cls, record):
        move_origin = record.move_origin
        if not move_origin or not hasattr(move_origin.raw, 'reference'):
            return ''
        return (move_origin.raw.reference and move_origin.render.reference
            or '')

    @classmethod
    def _grouped_records(cls, records):
        filtered = [
            (index, record) for index, record in enumerate(records)
            if cls._amount(record) != _ZERO]
        filtered.sort(key=lambda item: (
                item[1].raw.maturity_date is not None,
                item[1].raw.maturity_date or date.min,
                item[0]))
        return groupby(filtered, key=lambda item: item[1].raw.maturity_date)

    @classmethod
    def _header_row(cls):
        row = tr()
        row.add(th(_('Partner'), cls='col-partner'))
        row.add(th(_('Payment Type'), cls='col-payment-type'))
        row.add(th(_('Bank Account'), cls='col-bank-account'))
        row.add(th(_('Bank Name'), cls='col-bank-name'))
        row.add(th(_('Origin'), cls='col-origin'))
        row.add(th(_('Document'), cls='col-document'))
        row.add(th(_('Maturity Date'), cls='col-date text-right'))
        row.add(th(_('Amount'), cls='col-amount text-right'))
        row.add(th(_('Aggregated Amount'),
                cls='col-aggregated text-right'))
        return row

    @classmethod
    def _group_table(cls, maturity_date, lines, accumulated):
        total_maturity = sum((cls._amount(line) for line in lines), _ZERO)
        accumulated += total_maturity

        group_table = table(cls='forecast-table')
        group_table.add(thead(cls._header_row()))

        body = tbody(cls='forecast-body')
        for line in lines:
            amount = cls._amount(line)
            row = tr()
            row.add(td(line.party.render.name if line.party else '',
                    cls='col-partner'))
            row.add(td(line.payment_type.render.name if line.payment_type else '',
                    cls='col-payment-type'))
            row.add(td(cls._bank_account_number(line), cls='col-bank-account'))
            row.add(td(cls._bank_name(line), cls='col-bank-name'))
            row.add(td(cls._origin(line), cls='col-origin'))
            row.add(td(cls._document(line), cls='col-document'))
            row.add(td(html_render(maturity_date), cls='col-date text-right'))
            row.add(td(html_render(amount), cls='col-amount text-right'))
            row.add(td('', cls='col-aggregated text-right'))
            body.add(row)
        group_table.add(body)

        footer = tfoot()
        totals_row = tr(cls='forecast-group-total')
        totals_row.add(td(_('Maturity date totals:'), colspan='7',
                cls='forecast-group-total-label'))
        totals_row.add(td(html_render(total_maturity),
                cls='col-amount text-right'))
        totals_row.add(td(html_render(accumulated),
                cls='col-aggregated text-right'))
        footer.add(totals_row)
        group_table.add(footer)
        return group_table, accumulated

    @classmethod
    def body(cls, action, data, records):
        container = div(cls='forecast-report')
        accumulated = _ZERO
        for maturity_date, grouped_records in cls._grouped_records(records):
            lines = [record for _, record in grouped_records]
            group_box = div(cls='forecast-group')
            group_table, accumulated = cls._group_table(
                maturity_date, lines, accumulated)
            group_box.add(group_table)
            container.add(group_box)
        return container
