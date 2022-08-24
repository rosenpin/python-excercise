### ASSUMPTIONS ###
"""
* CSV is ordered by id field
* Each CSV row is valid (no empty cells, cells are in uniform format)
* No order ID = -1
* No duplications in sellAllToAll_accounts
"""

### NOTES & TODOs ###
"""
* There is an additional validation check that can be done regarding the order time. If 2 orders have the same ID but have 
     different checkout time, we should raise an error.
* Strings should be extracted to consts
* Files paths should be exported to CLI arguments
* Should add support for situation where orders appear on one CSV but not on the other
"""

import jsons

import formatters
import parser

from consts import *

DEFAULT_ID = -1
OUTPUT_FILE = "output.json"


class Order:
    orderId: str
    checkoutTime: int = 0
    amountUSD: float = 0
    cartItems = [parser.Item]
    accountOwner: parser.Owner = None

    def __init__(self, orderId: str, owner: parser.Owner, order_amount: float):
        self.orderId = orderId
        self.accountOwner = owner
        self.amountUSD = order_amount
        self.cartItems = []


def create_base_order_item(order) -> Order:
    if not parser.is_accounts_order(order):
        raise Exception("Unexpected format detected when expected main order item for order id %s" % order.orderId)

    return Order(order[ORDER_ID], parser.parse_account_owner(order), order[AMOUNT])


def add_item_to_order(base_order: Order, order: dict):
    if not parser.is_main_order(order):
        raise Exception("Unexpected format detected when expected main order item for order id %s" % base_order.orderId)

    base_order.cartItems.append(parser.parse_order_item(order))
    base_order.checkoutTime = order[CHECKOUT_TIME]


def append_order_to_file(order):
    with open(OUTPUT_FILE, 'a+') as o:
        o.write(jsons.dumps(order))


def validate_order(order: Order):
    order_sum = 0
    for item in order.cartItems:
        order_sum = round(order_sum + item.price * item.quantity)

    if float(order.amountUSD) != order_sum:
        print("Order {id} invalid. Item price sum ({sum}) doesn't match order full amount ({fullAmount})"
              .format(id=order.orderId, sum=order_sum, fullAmount=order.amountUSD))


def main():
    accounts_csv = parser.Reader("./assets/sellAllToAll_accounts.csv", formatters.FORMATTERS.get("accounts"))
    main_csv = parser.Reader("./assets/sellAllToAll_orders_main.csv", formatters.FORMATTERS.get("main"))

    main_order_dict = parser.get_order_from_row(main_csv, next(main_csv.reader))

    for account_row in accounts_csv.reader:
        order_dict = parser.get_order_from_row(accounts_csv, account_row)
        current_order = create_base_order_item(order_dict)

        while main_order_dict[ORDER_ID] == current_order.orderId:
            add_item_to_order(current_order, main_order_dict)
            main_order_dict = parser.get_order_from_row(main_csv, next(main_csv.reader))

        validate_order(current_order)
        append_order_to_file(current_order)


if __name__ == "__main__":
    main()
