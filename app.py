#!/usr/bin/env python3
"""A Store Inventory"""

import csv, sys, os, time

from peewee import *
from datetime import date, datetime
from collections import OrderedDict
from playhouse.shortcuts import model_to_dict

db = SqliteDatabase('inventory.db')

class Product(Model):
    """Define product categories"""
    product_id = AutoField()
    product_name = TextField()
    product_quantity = IntegerField(default=0)
    product_price = IntegerField()
    date_updated = DateTimeField()

    class Meta:
        """Configuration attributes"""
        database = db


def initialize():
    """Create the database if it doesn't exist"""
    db.connect()
    db.create_tables([Product], safe=True)

def read_from_CSV():
    """Read the CSV and call add to database function"""
    with open('inventory.csv', newline='') as csvfile:
        productreader = csv.DictReader(csvfile, delimiter=',')
        products = list(productreader)
        for product in products:
            add_entry(product)

def backup_CSV():
    """Create a backup of the CSV file"""
    try:
        with open('a.csv', mode='w', newline='') as csv_file:
            fieldnames = ['product_id', 'product_name', 'product_quantity', 'product_price', 'date_updated']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

            products = Product.select().order_by(Product.product_id.asc())
            for product in products:
                writer.writerow(model_to_dict(product))
        clear()
        print("\nAll products have now successfully been stored in the CSV file 'a.csv'\n")
    except PermissionError:
        clear()
        print("\nA file named 'a.csv' is currently in use. Please close it and try again.\n")

  
def get_input(prompt, numeric=False):
    """Get valid user input"""
    UserInputOK = False
    while not UserInputOK:
        Inputy = input(prompt)
        if numeric:
            if not Inputy.isalpha() and len(Inputy) != 0:
                UserInputOK = True
            else:
                print("The input cannot be empty and should be a number.")
        elif len(Inputy) != 0:
            UserInputOK = True
        else:
            print("The input cannot be empty")
    return str(Inputy)

def add_entry(prod_dict={}):
    """Add an entry to database"""
    #If no info provided then store product info from user in dictionary
    #(Else the provided dictioinary is used)
    user = False
    if prod_dict == {}:
        user = True
        print("True")
        prod_dict['product_name'] = get_input("\nPlease, input the product name: ")
        prod_dict['product_quantity'] = get_input("Please, input the quantity: ", True)
        prod_dict['product_price'] = get_input("Please, input the price: ")
        prod_dict['date_updated'] = str(datetime.strftime(date.today(),"%m.%d.%Y"))

    #Clean up the data (Standardised data is assumed.
        #Alternatively various exceptions should be caught here.)
    for cat, val in prod_dict.items():
        print(cat,val)
    for cat, val in prod_dict.items():
        if cat == 'product_price':
            #if the first character is not a number and the price is at least 2 characters long
            #(catches all kinds of currency indicators; In a production environment
            #it probably should be verified that currencies are used consistently)
            if not val[0].isnumeric() and len(val)>1:
                va = int(round(float(val[1:])*100))
            #in case there's a currency indicator only
            elif not val[0].isnumeric():
                va = 0
            else:
                #if no currency indicator
                va = int(round(float(val)*100))
        elif cat == 'date_updated':
            if '/' in val:
                va = val.replace('/','.')
            else:
                va = val
            #Parse string to datetime
            va = datetime.strptime(va,"%m.%d.%Y")
        else:
            va = val
        prod_dict[cat] = va

    pr_ex = product_exists(prod_dict['product_name'])
    #Add data from dictionary to database if:
    if not pr_ex:
        ##product does not exist
        Product.create(**prod_dict)
        if user:
            print(f"\nYou just entered a new product in the database:\n"
                  f"{prod_dict['product_quantity']} {prod_dict['product_name']}(s) "
              f"at a price of {prod_dict['product_price']} cents.\n")
    else:
        ##product is newer or has same date_updated
        if prod_dict['date_updated'] >= pr_ex:
            delete_product(prod_dict['product_name'])
            Product.create(**prod_dict)
            if user:
                print(f"\nYou just updated a product in the database:\n"
                  f"{prod_dict['product_quantity']} {prod_dict['product_name']}(s) "
                  f"at a price of {prod_dict['product_price']} cents.\n")
    print(63*'#')
    for cat, val in prod_dict.items():
        print(cat,val)
    print(63*'#')
    prod_dict = {}
    print(63*'#')
    for cat, val in prod_dict.items():
        print(cat,val)
    print(63*'#')

def view_products():
    """View previous entries."""
    products = Product.select().order_by(Product.date_updated.desc())

    product_not_found = True
    while product_not_found:
        search_query = int(get_input("\nPlease, input a product ID: ", True))
        for product in products:
            if search_query == product.product_id:
                print(f"""\nID: {product.product_id}, Updated: {datetime.strftime(product.date_updated,"%d.%m.%Y")}, """
                        f"""Product name: {product.product_name}, Product quantity: {product.product_quantity}, """
                      f"""Product price (cents): {product.product_price}\n""")
                return
        print("\nA product with this id was not found in the database. Please enter another number.")

def delete_product(product_name):
    """Delete product from database"""
    product = Product.get(Product.product_name == product_name)
    product.delete_instance()

def product_exists(product_name):
    """Check if product already in database"""
    #Returns none if not in database; Returns date last updated if it is as datetime
    products = Product.select().order_by(Product.date_updated.desc())
    products = products.where(Product.product_name == product_name)

    if len(products) > 0:
        return list(products)[0].date_updated
    else:
        return None

def clear():
    """Clear screen"""
    #This function was taken from a TeamTreehouse course
    #os.system('cls' if os.name == 'nt' else 'clear')
    pass

def menu_loop():
    """Show the menu"""
    #This function was taken from a TeamTreehouse course: Making a diary app
    choice = None

    menu = OrderedDict([
    ('A', add_entry),
    ('V', view_products),
    ('B', backup_CSV),
    ])
    
    while choice != 'Q':
        clear()
        print("Enter 'q' to quit.")
        for key, value in menu.items():
            print('{}) {}'.format(key, value.__doc__))
        choice = input('\nAction: ').upper().strip()
        if choice in menu.keys():
            clear()
            menu[choice]()
        elif choice != 'Q':
            print('\nThat is not a valid input. Please try again.\n')


if __name__ == '__main__':
    initialize()
    read_from_CSV()
    menu_loop()
    print("\nThank you for using Sebastiaan's Store Inventory program...\n")
    time.sleep(2)
    sys.exit()
