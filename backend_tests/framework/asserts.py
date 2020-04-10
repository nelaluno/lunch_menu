from hamcrest import assert_that, equal_to


def assert_data_are_equal(data):
    faults = {}
    for key, values in data.items():
        try:
            assert_that(values[0], equal_to(values[1]))
        except AssertionError:
            faults[key] = values
    if faults:
        raise AssertionError(faults)
