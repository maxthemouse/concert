import unittest
from concert.quantities import q, numerator_units, denominator_units


class TestUnits(unittest.TestCase):

    def setUp(self):
        self.quantity = 1.23 * q.deg * q.hour / q.m

    def test_numerator_units(self):
        num = numerator_units(self.quantity)
        assert len(num.units) == 2
        assert 'degree' in num.units
        assert 'hour' in num.units

    def test_denominator_units(self):
        den = denominator_units(self.quantity)
        assert len(den.units) == 1
        assert 'meter' in den.units
