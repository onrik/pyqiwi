# Pyqiwi
[![Build Status](https://travis-ci.org/onrik/pyqiwi.svg?branch=master)](https://travis-ci.org/onrik/pyqiwi)
[![Coverage Status](https://coveralls.io/repos/github/onrik/pyqiwi/badge.svg?branch=master)](https://coveralls.io/github/onrik/pyqiwi?branch=master)

Lib for [QIWI](https://qiwi.com/) payment system


Installation
------------

    pip install pyqiwi


Usage
------------

```python
from decimal import Decimal
from datetime import datetime, timedelta

from pyqiwi import Qiwi


qiwi = Qiwi('<shop_id>', '<app_id>', '<app_password>', '<notifications_password>')

qiwi.create_invoice(
    invoice_id='101',  # Must be unique for your shop
    amount=Decimal('22.00'),
    currency='RUB',
    comment='Order #101', 
    user='tel:+79998887766',
    lifetime=datetime.now()+timedelta(hours=1),  # Must be in Europe/Moscow timezone
)

print 'Invoice info:', qiwi.get_invoice('101')
print 'To pay invoice go to:', qiwi.get_invoice_url('101')
