# Pyqiwi
Lib for QIWI payment system


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

print 'Invoice info:', qiwi.create_invoice('101')
print 'To pay invoice go to:', qiwi.get_invoice_url('101')
