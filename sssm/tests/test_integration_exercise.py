# -*- coding: utf-8 -*-

import unittest
from datetime import datetime, timedelta
from sssm import Exchange, CommonStock, PreferredStock, Trade, Action


class TestIntegrationExercise(unittest.TestCase):
    def test_exercise(self):
        gbce = Exchange()
        stocks = {
            'TEA': CommonStock('TEA', last_div=0, par_val=100),
            'POP': CommonStock('POP', last_div=8, par_val=100),
            'ALE': CommonStock('ALE', last_div=23, par_val=60),
            'GIN': PreferredStock('GIN', last_div=8, fixed_div=0.02, par_val=100),
            'JOE': CommonStock('JOE', last_div=13, par_val=250)
        }
        # Req. 2.a.i
        pop_dividend_yield = stocks['POP'].div_yield(price=100)
        self.assertEqual(0.08, pop_dividend_yield)

        gin_dividend_yield = stocks['GIN'].div_yield(price=100)
        self.assertEqual(0.02, gin_dividend_yield)

        # Req. 2.a.ii
        pop_pe_ratio = stocks['POP'].pe_ratio(price=100)
        self.assertEqual(12.5, pop_pe_ratio)

        # Req. 2.a.iii
        gbce.record_trade(Trade(stocks['TEA'], 1000, Action.buy, 110))
        gbce.record_trade(Trade(stocks['TEA'], 2000, Action.buy, 105))
        gbce.record_trade(Trade(stocks['GIN'],  200, Action.buy,  80))
        self.assertEqual(3, len(gbce.trades))
        self.assertTrue(all(t.timestamp >= datetime.utcnow() - timedelta(seconds=0.1)
                            for t in gbce.trades))

        # Req. 2.a.iv
        tea_price = gbce.price_by_stock('TEA', duration=5*60)
        self.assertAlmostEqual(106.6666667, tea_price)

        gin_price = gbce.price_by_stock('GIN', duration=5*60)
        self.assertAlmostEqual(80, gin_price)

        # Req. 2.b
        gbce_index = gbce.all_share_index(duration=5*60)
        self.assertAlmostEqual(92.3760431, gbce_index)  # sqrt(106.67 * 80)