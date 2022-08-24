import atexit
import csv
from typing.io import TextIO

from consts import *
import formatters


class Item:
    price: float
    quantity: int
    name: str

    def __init__(self, price: float, quantity: int, name: str) -> None:
        self.price = price
        self.quantity = quantity
        self.name = name


def parse_order_item(order) -> Item:
    return Item(
        float(order[ITEM_PRICE]),
        int(order[ITEM_QUANTITY]),
        order[ITEM_NAME])


class Owner:
    firstName: str
    lastName: str
    email: str
    accountId: str

    def __init__(self, firstName: str, lastName: str, email: str, accountId: str):
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.accountId = accountId


def parse_account_owner(order) -> Owner:
    return Owner(
        order[FIRST_NAME],
        order.get(LAST_NAME),
        order.get(EMAIL),
        order.get(ACCOUNT_ID)
    )


def parse_order(headers, row):
    order = {}
    for i in range(len(headers)):
        order[headers[i]] = row[i]
    return order


class Reader:
    source: TextIO = None
    reader = None
    headers = None
    formatter = None
    formatted_headers = None

    def __init__(self, path: str, formatter):
        self.source = open(path)
        atexit.register(self.source.close)

        self.reader = csv.reader(self.source, delimiter=",", quotechar='"')
        self.headers = next(self.reader, None)
        self.formatter = formatter
        if not self.formatter:
            raise Exception("No formatter found")

        self.formatted_headers = formatters.format_headers(self.formatter, self.headers)


def is_main_order(order):
    return all(i in order for i in [ORDER_ID, CHECKOUT_TIME, ITEM_NAME, ITEM_PRICE, ITEM_QUANTITY])


def is_accounts_order(order):
    return all(i in order for i in [ORDER_ID, FIRST_NAME, LAST_NAME, EMAIL, ACCOUNT_ID, AMOUNT])


def get_order_from_row(reader: Reader, row: list[str]) -> dict:
    formatters.format_values(reader.formatter, reader.headers, row)
    return parse_order(reader.formatted_headers, row)
