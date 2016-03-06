# -*- coding: utf-8 -*-

"""
Super Simple Stock Market (SSSM) module for recording trades on a stock exchange and
calculating prices and indexes

Modules contains the following principal classes:

 * Exchange: records trades
 * Trade: a trade - buy or sell
 * Stock, incl. CommonStock and PreferredStock: a stock to trade in
"""

from enum import Enum
from datetime import datetime, timedelta
from operator import attrgetter, mul
from functools import reduce
from itertools import groupby
import collections


class Stock(object):
    """
    A stock that can be traded on the Global Beverage Corporation Exchange

    Should be sub-classed for common and preferred stock.
    """

    def __init__(self, symbol, last_div, par_val, fixed_div=None):
        #: Stock symbol, e.g. ``TEA``
        self.symbol = symbol.upper()
        #: Last dividend, in pence
        self.last_div = last_div
        #: Par value, in pence
        self.par_val = par_val
        #: Fixed dividend, percentage
        self.fixed_div = fixed_div

    def __repr__(self):
        return "<Stock object `{}`>".format(self.symbol)

    def div_yield(self, price):
        """
        Calculate the dividend yield for a given stock price

        :param price: stock price, in pence
        :type price: int or float
        :return: dividend yield
        :rtype: float
        """
        raise NotImplementedError()

    def pe_ratio(self, price):
        """
        Calculate the P/E ratio for a given stock price

        :param price: stock price, in pence
        :type price: int or float
        :return: P/E ratio
        :rtype: float
        """
        return 1 / self.div_yield(price)


class CommonStock(Stock):
    """A common stock"""

    def __repr__(self):
        return "<CommonStock object `{}`>".format(self.symbol)

    def div_yield(self, price):
        return self.last_div / price


class PreferredStock(Stock):
    """A preferred stock"""

    def __repr__(self):
        return "<PreferredStock object `{}`>".format(self.symbol)

    def div_yield(self, price):
        return self.fixed_div * self.par_val / price


class Action(Enum):
    """Direction of a trade (buy or sell)"""
    buy = 1
    sell = -1


class Trade(object):
    """A trade of a stock"""

    def __init__(self, stock, quantity, action, price):
        #: Stock to buy or sell, :class:`sssm.Stock` object
        # Alternatively we could just record the stock's symbol as a (foreign) key
        self.stock = stock
        #: Quantity to buy or sell
        self.quantity = quantity
        #: Either ``sssm.Action.buy`` or ``sssm.Action.sell``
        self.action = action
        #: Stock price
        self.price = price
        #: Date/time of trade (UTC)
        # Assume timestamp always correct when object created. Alternatively, this could
        # be implemented in the :func:`sssm.Exchange.record_trade` method if it's the role
        # of the exchange to timestamp trades.
        self.timestamp = datetime.utcnow()

    def __repr__(self):
        return "<Trade object: {} {} of stock `{}`>".format(self.action, self.quantity,
                                                            self.stock.symbol)

    @staticmethod
    def vol_weighted_price(trades):
        """
        Calculate the volume weighted price for a sequence of trades

        :param trades: trades to obtained the averaged price over
        :type trades: list of :class:`sssm.Trade`
        :return: volume weighted price
        :rtype: float
        """
        return (sum(t.price * t.quantity for t in trades) /
                sum(t.quantity for t in trades))


class Exchange(object):
    """A stock exchange"""

    def __init__(self):
        #: List of trades
        self.trades = collections.deque()

    def __repr__(self):
        return "<Exchange object: {} trades>".format(len(self.trades))

    def record_trade(self, trade):
        """
        Record a trade on the stock exchange

        :param trade: a single trade (buy or sell) of stocks
        :type trade: :class:`sssm.Trade`
        """
        self.trades.append(trade)

    def price_by_stock(self, symbol, duration):
        """
        Calculate the volume weighted average price of a stock over a certain duration

        :param symbol: stock symbol, e.g. ``TEA``
        :type symbol: str
        :param duration: duration to average over, in seconds, e.g. 300 would return the
                         average traded price over the last 5 minutes
        :type duration: int
        :return: volume weighted average trading price (returns ``None`` if there are no
                 trades for this stock)
        :rtype: float or None
        """
        trades = [t for t in self.trades
                  if t.stock.symbol == symbol.upper()
                  and t.timestamp >= datetime.utcnow() - timedelta(seconds=duration)]
        if trades:
            return Trade.vol_weighted_price(trades)
        else:
            return None

    def all_share_index(self, duration):
        """
        Calculate the exchange's All Share Index over a certain duration

        :param duration: duration to average over, in seconds, e.g. 300 would return the
                         index over the last 5 minutes
        :type duration: int
        :return: the All Share Index (returns ``None`` if there are no trades at all)
        :rtype: float or None
        """

        # sorting needed for `groupby` function
        trades = sorted([t for t in self.trades
                         if t.timestamp >= datetime.utcnow()
                                           - timedelta(seconds=duration)],
                        key=attrgetter('stock.symbol'))
        if trades:
            stock_groups = groupby(trades, key=attrgetter('stock.symbol'))
            prices = [Trade.vol_weighted_price(list(trades)) for symbol, trades in
                      stock_groups]
            return reduce(mul, prices) ** (1 / len(prices))
        else:
            return None
