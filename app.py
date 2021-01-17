#!/usr/bin/env python3
"""A Store Inventory"""

import datetime
import sys
import os
import csv
from collections import OrderedDict

from peewee import *

db = SqliteDatabase('inventory.db')

class Product(Model):
##    product_id = AutoField()
    product_name = TextField()
##    product_quantity = IntegerField(default=0)
##    product_price = IntegerField()
##    date_updated = DateTimeField()
    
    class Meta:
        database = db
            
def initialize():
    """Create the database and the table if they don't exist."""
    db.connect()
    db.create_tables([Product], safe=True)


##def view_entries(search_query=None):
##    """View previous entries."""
##    entries = Product.select().order_by(Product.product_id.desc())
##    if search_query:
##        entries = entries.where(Product.content.contains(search_query))


##def add_entry(cat, inp):
##    """Add an entry."""
##    if cat == '' and inp == '':
##        print("Enter your entry. Press ctrl+d when finished.")
##        inp = sys.stdin.read().strip()
##        
##    if cat:
##        Product.create(cat=inp)

##menu = OrderedDict([
##    ('a', add_entry),
##    ('v', view_entries),
##    ('s', search_entries),
##])

##def read_from_CSV():
##    with open('inventory.csv', newline='') as csvfile:
##        productreader = csv.DictReader(csvfile, delimiter=',')
##        rows = list(productreader)
##        for row in rows[1:]:
##            for k, v in row.items():
##                if k == 'product_name':
##                    print(k)
##                    print(v)
##                    add_entry(k, v)


def read_from_CSV2():
    with open('inventory.csv', newline='') as csvfile:
        productreader = csv.DictReader(csvfile, delimiter=',')
        rows = list(productreader)
        for row in rows[1:]:
            for k, v in row.items():
                if k == 'product_name':
                    print(k)
                    print(v)
                    try:
                        Product.create(k=v)
                    except IntegrityError:
                        print(k)
                        product_record = Product.get(k=v)
                        product_record.save()

if __name__ == '__main__':
    initialize()
    read_from_CSV2()
##    menu_loop()
    
