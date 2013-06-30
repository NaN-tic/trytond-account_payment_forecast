#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.
from trytond.pool import Pool
from .forecast import *


def register():
    Pool.register(
        ForecastReport,
        module='account_payment_forecast', type_='report')
