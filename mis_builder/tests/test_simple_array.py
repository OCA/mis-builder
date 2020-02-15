# Copyright 2014 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import doctest

from ..models import simple_array


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(simple_array))
    return tests
