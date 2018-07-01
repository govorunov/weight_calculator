#!/usr/bin/env python3
"""
Unit tests for weight_calculator
"""

__author__ = "Yaroslav Hovorunov"
__version__ = "0.1.0"
__license__ = "MIT"

import unittest
import csv
from weight_calculator import *


class TestReadDataFunctions(unittest.TestCase):
    """ Testing weight_calculator.read_funds_data """

    def test_assignment_data(self):
        """ Testing original assignment data """
        data = """A,B,1000
            A,C,2000
            B,D,500
            B,E,250
            B,F,250
            C,G,1000
            C,H,1000"""
        reader = csv.reader(data.splitlines(), skipinitialspace=True)
        funds, root_funds = read_funds_data(reader)
        self.assertSetEqual(root_funds, set("A"))
        self.assertSetEqual(set(funds.keys()), {'A','B','C','D','E','F','G','H'})

    def test_no_root(self):
        data = """A,B,1000
            A,C,2000
            B,D,500
            B,E,250
            B,F,250
            C,G,1000
            C,H,1000
            C,A,500"""
        reader = csv.reader(data.splitlines(), skipinitialspace=True)
        funds, root_funds = read_funds_data(reader)
        self.assertSetEqual(root_funds, set())

    def test_duplicate_entry(self):
        data = """A,B,1000
            A,C,2000
            B,D,500
            B,E,250
            B,F,250
            C,G,1000
            C,H,1000
            C,A,500
            B,E,500"""
        reader = csv.reader(data.splitlines(), skipinitialspace=True)
        self.assertRaises(DataError, read_funds_data, reader)

    def test_incorrect_format_less(self):
        data = """A,B,1000
            A,C,2000
            B,D
            B,E,250
            B,F,250"""
        reader = csv.reader(data.splitlines(), skipinitialspace=True)
        self.assertRaises(DataError, read_funds_data, reader)

    def test_incorrect_format_more(self):
        data = """A,B,1000
            A,C,2000
            B,D,500,W
            B,E,250
            B,F,250"""
        reader = csv.reader(data.splitlines(), skipinitialspace=True)
        self.assertRaises(DataError, read_funds_data, reader)

    def test_incorrect_format_value(self):
        data = """A,B,1000
            A,C,2000
            B,D,
            B,E,250
            B,F,250"""
        reader = csv.reader(data.splitlines(), skipinitialspace=True)
        self.assertRaises(ValueError, read_funds_data, reader)


class TestCalculateWeightsFunctions(unittest.TestCase):
    """ Testing weight_calculator.calculate_weights """

    def test_assignment_data(self):
        """ Testing original assignment data """
        data = """A,B,1000
            A,C,2000
            B,D,500
            B,E,250
            B,F,250
            C,G,1000
            C,H,1000"""
        reader = csv.reader(data.splitlines(), skipinitialspace=True)
        funds, root_funds = read_funds_data(reader)
        value, weights = calculate_weights(funds, "A")
        self.assertEqual(value, 3000)
        self.assertSetEqual(set(weights.keys()), {'D','E','F','G','H'})
        test_list = [round(float(elem), 3) for elem in weights.values()]
        self.assertListEqual(test_list, [0.167, 0.083, 0.083, 0.333, 0.333])

    def test_complex_path(self):
        """ Testing original assignment data """
        data = """A,B,500
                A,C,2100
                B,D,500
                B,E,250
                B,F,250
                C,G,500
                C,H,1000
                C,B,500
                C,D,100"""
        reader = csv.reader(data.splitlines(), skipinitialspace=True)
        funds, root_funds = read_funds_data(reader)
        value, weights = calculate_weights(funds, "A")
        self.assertEqual(value, 2600)
        self.assertSetEqual(set(weights.keys()), {'D','E','F','G','H'})
        test_list = [round(float(elem), 3) for elem in weights.values()]
        self.assertListEqual(test_list, [0.135,0.096,0.096,0.192,0.385])

    def test_looped_data(self):
        """ Testing original assignment data """
        data = """A,B,1000
            A,C,2000
            B,D,500
            B,E,250
            B,F,250
            D,B,500
            C,G,1000
            C,H,1000"""
        reader = csv.reader(data.splitlines(), skipinitialspace=True)
        funds, root_funds = read_funds_data(reader)
        self.assertRaises(DataError, calculate_weights, funds, "A")


if __name__ == '__main__':
    unittest.main()