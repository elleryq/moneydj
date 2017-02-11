# -*- coding: utf-8 -*-
"""
Get funds information from MoneyDJ.
"""
from __future__ import unicode_literals, print_function
import re
from itertools import islice
from collections import namedtuple
import requests
from pyquery import PyQuery


FundCompany = namedtuple('FundCompany', [
    'name', 'code'
])


LocalFund = namedtuple('LocalFund', [
    'name',
    'link',
    'net_value_date',
    'net_value',
    'currency',
    'change',
    'change_percentage'])


ForeignFund = namedtuple('ForeignFund', [
    'name',
    'link',
    'net_value_date',
    'net_value',
    'currency',
    'last_six_month_change',
    'last_year_change'])


def get_local_funds_js():
    """
    Get funds string from js.

    本來打算從 HTML 取得，但發現網站原本的 HTML 裡只有幾個 X ，資料是由
    javascript 填入的。
    """
    taiwan_funds_endpoint = "https://www.moneydj.com/funddj/js/yfundjs.djjs"
    req = requests.get(taiwan_funds_endpoint)
    req.encoding = "big5"
    return req.text


def extract_local_funds_str(js_str):
    """
    Extract the string contained funds information.

    The string variable contained funds information is 'tfund_corp',
    so I use regular expression to find the string and extract it.
    """
    pattern = re.compile(r'var\ tfund_corp=\"(?P<funds>.*)#\";')
    found = pattern.search(js_str)
    if found:
        funds_str = found.group('funds')
        return funds_str
    return ""


def get_local_fund_companies():
    """Get fund company and codes."""
    funds_str = extract_local_funds_str(get_local_funds_js())

    # extract fail.
    if not funds_str:
        return

    # The string format is "code#name#code#name#...."
    funds = funds_str.split('#')
    start = 0
    while True:
        if start >= len(funds):
            break
        yield FundCompany(*islice(funds, start, start + 2))
        start = start + 2


def extract_local_fund(row_element):
    """Extract fund information from table row."""
    host_url = 'https://www.moneydj.com'
    rowq = PyQuery(row_element)
    name = rowq("td[myClass='t3t1c1']").text()
    anchor = rowq("td[myClass='t3t1c1'] > a")
    link = ''.join([
        host_url, anchor.attr('href') if anchor else ''])
    cells = rowq("td")
    net_value_date = cells.eq(2).text()
    net_value = cells.eq(4).text()
    currency = cells.eq(3).text()
    change = cells.eq(5).text()
    change_percentage = cells.eq(6).text()
    return LocalFund(
        name, link,
        net_value_date, net_value, currency,
        change, change_percentage)


def get_local_funds():
    """
    Get local funds. 取得國內所有基金資料.

    Return Fund iterable.
    """
    base_url = "https://www.moneydj.com/funddj/ya/yp082000.djhtm"
    for code, name in get_local_fund_companies():
        endpoint = "{base_url}?a={code}".format(
            base_url=base_url,
            code=code
        )
        req = requests.get(endpoint)
        req.encoding = "big5"
        pq = PyQuery(req.text)
        funds_table = pq("table#oMainTable > tbody > tr")
        for row in funds_table:
            fund = extract_local_fund(row)
            yield fund


def get_foreign_funds_js():
    """
    Get foreign funds string from js.

    本來打算從 HTML 取得，但發現網站原本的 HTML 裡只有幾個 X ，資料是由
    javascript 填入的。
    """
    foreign_funds_endpoint = "https://www.moneydj.com/funddj/js/wfundjs.djjs"
    req = requests.get(foreign_funds_endpoint)
    req.encoding = "big5"
    return req.text


def extract_foreign_funds_str(js_str):
    """
    Extract the string contained funds information.

    The string variable contained funds information is 'tfund_corp',
    so I use regular expression to find the string and extract it.
    """
    pattern = re.compile(r'var\ wfund_corp=\"(?P<funds>.*)\$\";')
    found = pattern.search(js_str)
    if found:
        funds_str = found.group('funds')
        return funds_str
    return ""


def get_foreign_fund_companies():
    """Get fund company and codes."""
    funds_str = extract_foreign_funds_str(get_foreign_funds_js())

    # extract fail.
    if not funds_str:
        return

    # The string format is "code$name$code$name$...."
    funds = funds_str.split('$')
    start = 2  # skip first 2 items
    while True:
        if start >= len(funds):
            break
        yield FundCompany(*islice(funds, start, start + 2))
        start = start + 2


def extract_foreign_fund(row_element):
    """Extract fund information from table row."""
    host_url = 'https://www.moneydj.com'
    rowq = PyQuery(row_element)
    name = rowq("td[myClass='t3t1c1']").text()
    anchor = rowq("td[myClass='t3t1c1'] > a")
    link = ''.join([
        host_url, anchor.attr('href') if anchor else ''])
    cells = rowq("td")
    net_value_date = cells.eq(1).text()
    net_value = cells.eq(3).text()
    currency = cells.eq(2).text()
    last_six_month_change = cells.eq(4).text()
    last_year_change = cells.eq(5).text()
    return ForeignFund(
        name, link,
        net_value_date, net_value, currency,
        last_six_month_change, last_year_change)


def get_foreign_funds():
    """
    Get foreign funds. 取得海外所有基金資料.

    Return Fund iterable.
    """
    base_url = "https://www.moneydj.com/funddj/ya/yp081001.djhtm"
    for code, name in get_foreign_fund_companies():
        endpoint = "{base_url}?a={code}&ff=1".format(
            base_url=base_url,
            code=code
        )
        req = requests.get(endpoint)
        req.encoding = "big5"
        pq = PyQuery(req.text)
        funds_table = pq("table#oMainTable > tbody > tr")
        for row in funds_table:
            fund = extract_foreign_fund(row)
            yield fund
