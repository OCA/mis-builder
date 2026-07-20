# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import doctest
import io
import logging

import openpyxl

from odoo import api
from odoo.tests import BaseCase, tagged

_logger = logging.getLogger(__name__)
_test_logger = logging.getLogger("odoo.tests")


def _zip(iter1, iter2):
    i = 0
    iter1 = iter(iter1)
    iter2 = iter(iter2)
    while True:
        i1 = next(iter1, None)
        i2 = next(iter2, None)
        if i1 is None and i2 is None:
            return
        yield i, i1, i2
        i += 1


def assert_matrix(matrix, expected):
    for i, row, expected_row in _zip(matrix.iter_rows(), expected):
        if row is None and expected_row is not None:
            raise AssertionError("not enough rows")
        if row is not None and expected_row is None:
            raise AssertionError("too many rows")
        for j, cell, expected_val in _zip(row.iter_cells(), expected_row):
            assert (cell and cell.val) == expected_val, (
                f"{cell and cell.val} != {expected_val} in row {i} col {j}"
            )


@tagged("doctest")
class OdooDocTestCase(BaseCase):
    """
    We need a custom DocTestCase class in order to:
    - define test_tags to run as part of standard tests
    - output a more meaningful test name than default "DocTestCase.runTest"
    """

    __qualname__ = "doctests for "

    def __init__(self, test):
        self.__test = test
        self.__name = test._dt_test.name
        super().__init__(self.__name)

    def __getattr__(self, item):
        if item == self.__name:
            return self.__test


def load_doctests(module):
    """
    Generates a tests loading method for the doctests of the given module
    https://docs.python.org/3/library/unittest.html#load-tests-protocol
    """

    def load_tests(loader, tests, ignore):
        for test in doctest.DocTestSuite(module):
            tests.addTest(OdooDocTestCase(test))
        return tests

    return load_tests


def try_xlsx_report(
    cr, uid, rname, ids, data=None, context=None, our_module=None, report_type=None
):
    """Try to render a report <rname> with contents of ids

    This function should also check for common pitfalls of reports.

    this is inspired from the odoo.tools.test_reports.try_report specialiazed to xlsx
    """
    if context is None:
        context = {}
    _test_logger.info("  - Trying %s.create(%r)", rname, ids)

    env = api.Environment(cr, uid, context)

    res_data, res_format = env["ir.actions.report"]._render(rname, ids, data=data)

    if not res_data:
        raise ValueError(f"Report {rname} produced an empty result!")

    if res_format == "xlsx":
        return openpyxl.load_workbook(io.BytesIO(res_data), data_only=True)
    else:
        _logger.warning(
            'Report %s produced a "%s" chunk, cannot examine it', rname, res_format
        )
        return False

    _test_logger.info("  + Report %s produced correctly.", rname)
    return True
