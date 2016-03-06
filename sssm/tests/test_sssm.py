# -*- coding: utf-8 -*-

import unittest
from unittest.mock import Mock
from datetime import datetime
import sssm


class TestStock(unittest.TestCase):
    def test_create_stock(self):
        stock = sssm.Stock('TEA', last_div=0, par_val=100)
        self.assertEqual('TEA', stock.symbol)
        self.assertEqual(0, stock.last_div)
        self.assertEqual(100, stock.par_val)
        self.assertIsNone(stock.fixed_div)

    def test_create_stock_lowercase_sym(self):
        stock = sssm.Stock('tea', last_div=0, par_val=100)
        self.assertEqual('TEA', stock.symbol)

    def test_div_yield_not_implemented(self):
        stock = sssm.Stock('TEA', last_div=0, par_val=100)
        with self.assertRaises(NotImplementedError):
            stock.div_yield(price=100)

    def test_div_yield_common(self):
        stock = sssm.CommonStock('POP', last_div=8, par_val=100)
        self.assertEqual(0.08, stock.div_yield(price=100))

    def test_div_yield_preferred(self):
        stock = sssm.PreferredStock('POP', last_div=8, fixed_div=0.02, par_val=100)
        self.assertEqual(0.02, stock.div_yield(price=100))

    def test_pe_ratio_common(self):
        stock = sssm.CommonStock('POP', last_div=8, par_val=100)
        self.assertEqual(12.5, stock.pe_ratio(price=100))

    def test_pe_ratio_preferred(self):
        stock = sssm.PreferredStock('POP', last_div=8, fixed_div=0.02, par_val=100)
        self.assertEqual(50, stock.pe_ratio(price=100))


class TestTrade(unittest.TestCase):
    def test_create_buy_trade(self):
        stock = Mock()
        trade = sssm.Trade(stock=stock, quantity=20, action=sssm.Action.buy, price=100)
        self.assertEqual(stock, trade.stock)
        self.assertEqual(20, trade.quantity)
        self.assertEqual(sssm.Action.buy, trade.action)
        self.assertEqual(100, trade.price)
        # Just test if trade has been recorded less than 0.1 seconds aga
        self.assertLessEqual((trade.timestamp - datetime.utcnow()).total_seconds(), 0.1)

    def test_create_sell_trade(self):
        stock = Mock()
        trade = sssm.Trade(stock=stock, quantity=20, action=sssm.Action.sell, price=100)
        self.assertEqual(sssm.Action.sell, trade.action)

    def test_vol_weighted_price(self):
        stock = Mock()
        trades = [
            sssm.Trade(stock=stock, quantity=20, action=sssm.Action.buy, price=100),
            sssm.Trade(stock=stock, quantity=40, action=sssm.Action.buy, price=120)
        ]
        self.assertAlmostEqual(113.3333333, sssm.Trade.vol_weighted_price(trades))


class TestExchange(unittest.TestCase):
    def test_create_exchange(self):
        exchange = sssm.Exchange()
        self.assertEqual(0, len(exchange.trades))

    def test_record_trade(self):
        exchange = sssm.Exchange()
        trade = Mock()
        exchange.record_trade(trade)
        # Test that the last trade is the trade just recorded
        self.assertEqual(trade, exchange.trades[-1])

    def test_record_multiple_trades(self):
        exchange = sssm.Exchange()
        trades = [Mock(), Mock(), Mock()]
        for trade in trades:
            exchange.record_trade(trade)
        self.assertEqual(trades[2], exchange.trades[-1])
        self.assertEqual(3, len(exchange.trades))

    def test_vol_weighted_price_by_stock(self):
        exchange = sssm.Exchange()
        stock = Mock(symbol='TEA')
        exchange.trades = [
            sssm.Trade(stock=stock, quantity=20, action=sssm.Action.buy, price=100),
            sssm.Trade(stock=stock, quantity=40, action=sssm.Action.buy, price=120)
        ]
        self.assertAlmostEqual(113.3333333, exchange.price_by_stock('TEA', duration=5*60))

    def test_none_vol_weighted_price_by_stock(self):
        exchange = sssm.Exchange()
        self.assertIsNone(exchange.price_by_stock('TEA', duration=5*60))

    def test_vol_weighted_price_by_stock_duration(self):
        exchange = sssm.Exchange()
        stock = Mock(symbol='TEA')
        exchange.trades = [
            sssm.Trade(stock=stock, quantity=20, action=sssm.Action.buy, price=100),
            sssm.Trade(stock=stock, quantity=40, action=sssm.Action.buy, price=120)
        ]
        # Manually override the timestamp of a trade
        exchange.trades[0].timestamp = datetime(2000, 1, 1)
        self.assertAlmostEqual(120, exchange.price_by_stock('TEA', duration=5*60))

    def test_all_share_index(self):
        exchange = sssm.Exchange()
        exchange.trades = [
            sssm.Trade(stock=Mock(symbol='TEA'), quantity=20, action=sssm.Action.buy, price=100),
            sssm.Trade(stock=Mock(symbol='POP'), quantity=40, action=sssm.Action.buy, price=120)
        ]
        self.assertAlmostEqual(109.5445115, exchange.all_share_index(duration=5*60))

    def test_all_share_index_none(self):
        exchange = sssm.Exchange()
        self.assertIsNone(exchange.all_share_index(duration=5*60))
