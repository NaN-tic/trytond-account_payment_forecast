# This file is part account_payment_forecast module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import forecast


def register():
    Pool.register(
        forecast.ForecastReport,
        module='account_payment_forecast', type_='report')
