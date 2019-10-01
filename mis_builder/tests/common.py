# Copyright 2017-2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def setup_test_model(env, model_cls):
    model_cls._build_model(env.registry, env.cr)
    env.registry.setup_models(env.cr)
    env.registry.init_models(
        env.cr, [model_cls._name],
        dict(env.context, update_custom_fields=True)
    )


def teardown_test_model(env, model_cls):
    del env.registry.models[model_cls._name]
    env.registry.setup_models(env.cr)


def _zip(iter1, iter2):
    i = 0
    iter1 = iter(iter1)
    iter2 = iter(iter2)
    while True:
        i1 = next(iter1, None)
        i2 = next(iter2, None)
        if i1 is None and i2 is None:
            raise StopIteration()
        yield i, i1, i2
        i += 1


def assert_matrix(matrix, expected):
    for i, row, expected_row in _zip(matrix.iter_rows(), expected):
        if row is None and expected_row is not None:
            assert False, "not enough rows"
        if row is not None and expected_row is None:
            assert False, "too many rows"
        for j, cell, expected_val in _zip(row.iter_cells(), expected_row):
            assert (cell and cell.val) == expected_val, \
                "%s != %s in row %s col %s" % \
                (cell and cell.val, expected_val, i, j)
