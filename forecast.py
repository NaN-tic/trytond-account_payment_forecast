#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.
from trytond.pool import PoolMeta
from trytond.modules.jasper_reports.jasper import JasperReport

__all__ = ['ForecastReport']
__metaclass__ = PoolMeta


class ForecastReport(JasperReport):
    __name__ = 'account_payment_forecast.forecast'
