#!/usr/bin/env python3
"""
JPM Portfolio Weight Calculator
"""

__author__ = "Yaroslav Hovorunov"
__version__ = "0.1.0"
__license__ = "MIT"

import argparse
import logging
import csv
from collections import defaultdict
from decimal import Decimal


class DataError(Exception):
    """Incorrect data exception"""
    pass


class Fund:
    """
    Fund representation class
    values represent sub-funds this fund consists of
    and their values in the fund in the format of dictionary:
    {'Sub-fund Name': value}
    """

    def __init__(self):
        self.values = {}

    def __repr__(self):
        return str(self.values)


def read_data_from_list(funds_list) -> (defaultdict(Fund), set):
    """
    Reads data from a list or stream.

    :param funds_list: list of funds
    :return: A resulting graph structure.
    :raises: DataError, ValueError
    """
    funds = defaultdict(Fund)
    has_parent = set()  # Needed to find root funds
    for idx, row in enumerate(funds_list, start=1):
        if len(row) != 3:
            raise DataError("Incorrect data format at line {}".format(idx))
        parent = row[0]
        child = row[1]
        value = Decimal(float(row[2]))
        if not parent or not child:
            raise DataError("Incorrect data format at line {}".format(idx))
        if child not in funds[parent].values:
            funds[parent].values[child] = value
        else:
            raise DataError("Duplicate fund entry at line {}".format(idx))
        funds[child]  # Add child fund
        has_parent.add(child)

    # We need to find root nodes now. No warranty
    # first node in csv file is the root, as no warranty there
    # is only one root in data.
    root_nodes = funds.keys() - has_parent
    return funds, root_nodes


def calculate_weights(funds: dict, fund_name: str, visited=set()) -> (Decimal, defaultdict(Decimal)):
    """
    Recursively calculates weights of base funds in a given fund.
    Recursively normalzes weights for each level.
    Supports graphs, when base fund is included in root fund
    through different path.
    Detects loops in data to prevent infinite loops.

    :param funds: A graph containing funds and values
    :param fund_name: Current fund to start (root)
    :param visited: Counter to prevent looping
    :return: Absolute fund value and a dict of base funds weights, normalized
    """
    logging.debug("Calculating weights for fund {}".format(fund_name))
    if fund_name in visited:  # Check for loops in data graph
        raise DataError("Data is looped. Fund {} is both parent and child.".format(fund_name))
    fund = funds[fund_name]
    weights = defaultdict(Decimal)
    if len(fund.values) > 0:  # fund has sub-funds
        visited.add(fund_name)  # Count for loop check
        fund_value = sum(fund.values.values())  # Underlying value of fund
        logging.debug("Underlying value of fund {} is {}".format(fund_name, fund_value))
        for key, value in fund.values.items():  # for each sub-fund
            # RECURSION
            sub_value, sub_weights = calculate_weights(funds, key, visited)
            logging.debug("Calc weights of {} in {} returned {}:{}".format(
                key, fund_name, sub_value, sub_weights
            ))
            if len(sub_weights) == 0:  # Base fund.
                logging.debug("Fund {} is base fund".format(key))
                weights[key] = value / fund_value  # Adding its weight to dict
                logging.debug("Weight of fund {} in fund {} is {}".format(key, fund_name, weights[key]))
            else:  # sub-fund has children
                for wsf_name, wsf_weight in sub_weights.items():  # Cycle through sub-funds weights returned
                    # Normalize weights to the context of current fund
                    normalized_wsf_weight = wsf_weight * (value / fund_value)
                    logging.debug("Weight of fund {} in fund {} through {} is {}".format(
                        wsf_name,
                        fund_name,
                        key,
                        normalized_wsf_weight
                    ))
                    weights[wsf_name] = weights[wsf_name] + normalized_wsf_weight
        visited.remove(fund_name)  # Only check for loops inside the path
        return fund_value, weights
    else:
        return Decimal(0), defaultdict(Decimal)  # Base fund


def print_results(root_fund_name, weights, value, total_returns=None, weighted_returns=None):
    """

    :param root_fund_name:
    :param weights:
    :param value:
    :param total_returns:
    :param weighted_returns:
    :return:
    """
    if weighted_returns:
        for base_fund, weight in weights.items():
            print(f"{root_fund_name},{base_fund},{weight:.3F},{weighted_returns[base_fund]:.3F}")
    else:
        for base_fund, weight in weights.items():
            print(f"{root_fund_name},{base_fund},{weight:.3F}")


def main(args, loglevel):
    """
    Main function.
    :param args: List of arguments from argparse
    :param loglevel:
    :return:
    """
    logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)

    # Dictionary of all funds {'Fund Name': class Fund}
    funds = None
    returns = None

    # Set of root nodes, in case there is more than one in dataset
    root_nodes = None

    # Section that loads data
    try:
        # Open csv data file
        with open(args.data_file, 'r', newline='') as csvfile:
            # Read data from csv file
            funds_list = list(csv.reader(csvfile, delimiter=',', skipinitialspace=True))

        if len(funds_list[0]) == 4:  # We have end market values data
            # Calculate returns
            returns_list = [[i[0], i[1], float(i[3])-float(i[2])] for i in funds_list]
            funds_list = [[i[0], i[1], i[2]] for i in funds_list]
            returns, _ = read_data_from_list(returns_list)

        funds, root_nodes = read_data_from_list(funds_list)

        # Check resulting data
        if len(root_nodes) < 1:
            raise DataError("Data is looped, expected Tree or Forest")
        if len(funds) < 1:
            raise DataError("No funds to act on")

        # It is not clear if multiple roots are allowed
        # Since we can act on multiple roots lets just log warning for now.
        if len(root_nodes) > 1:
            logging.warning("Multiple roots found")
    except (DataError, ValueError) as err:
        logging.error("Cannot read file {} - {}".format(args.data_file, err))
        exit(1)
    except OSError as err:
        logging.error("Cannot open file {} - {}".format(args.data_file, err.strerror))
        exit(err.errno)
    except Exception:
        logging.exception("Unexpected error")
        exit(1)

    # Calculate fund weights
    for node in root_nodes:
        try:
            value, weights = calculate_weights(funds, node)
            if returns:
                total_returns, weighted_returns = calculate_weights(returns, node)
                print_results(node, weights, value, total_returns, weighted_returns)
            else:
                print_results(node, weights, value)
        except DataError as err:
            logging.error(err)
            exit(1)
        except Exception:  # Probably stack overflow
            logging.exception("Unexpected error")
            exit(1)


# Standard code to parse arguments and call the main() function to begin
# the program.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Calculates weights of funds in portfolio.")
    parser.add_argument(
        "data_file",
        help="A .csv file containing fund data to act on.")
    parser.add_argument(
        "-ev",
        nargs=1,
        metavar="end_values_file",
        help="A .csv file containing end market values to calculate weighted returns.")
    parser.add_argument(
        "-v",
        "--verbose",
        help="increase log verbosity",
        action="store_true")
    args = parser.parse_args()

    # Setup logging
    if args.verbose:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    main(args, loglevel)
