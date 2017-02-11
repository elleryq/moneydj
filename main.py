# -*- coding: utf-8 -*-
"""
Get funds information from MoneyDJ.
"""
from __future__ import unicode_literals, print_function
import os
import json

from moneydj import get_local_funds, get_foreign_funds


if __name__ == "__main__":
    if not os.path.exists("local_funds.json"):
        json.dump(
            [fund.__dict__ for fund in get_local_funds()],
            open('local_funds.json', 'wt'))
    else:
        print("already grabbed.")

    if not os.path.exists("foreign_funds.json"):
        json.dump(
            [fund.__dict__ for fund in get_foreign_funds()],
            open('foreign_funds.json', 'wt'))
    else:
        print("already grabbed.")
