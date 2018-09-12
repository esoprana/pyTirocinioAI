from progTiroc.ai import check
import pytest


@pytest.mark.parametrize("condition,value,expected", [
    ({
        'a__lt': 1
    }, {
        'a': 1
    }, False),
    ({
        'a__lt': 1
    }, {
        'a': -1
    }, True),
    ({
        'a__lt': 1
    }, {
        'a': 2
    }, False),
    ({
        'a__lt': 1
    }, {
        'a': 1.4
    }, False),
    ({
        'a__lt': 1
    }, {
        'a': 2.9
    }, False),
    ({
        'a__lt': 4
    }, {
        'a': 2
    }, True),
    ({
        'a__lt': 4
    }, {
        'a': 2.9
    }, True),
])
def test_single_lt(condition, value, expected):
    assert check(condition, value) == expected


@pytest.mark.parametrize("condition,value,expected", [
    ({
        'a__ge': 1
    }, {
        'a': 1
    }, not False),
    ({
        'a__ge': 1
    }, {
        'a': -1
    }, not True),
    ({
        'a__ge': 1
    }, {
        'a': 2
    }, not False),
    ({
        'a__ge': 1
    }, {
        'a': 1.4
    }, not False),
    ({
        'a__ge': 1
    }, {
        'a': 2.9
    }, not False),
    ({
        'a__ge': 4
    }, {
        'a': 2
    }, not True),
    ({
        'a__ge': 4
    }, {
        'a': 2.9
    }, not True),
])
def test_single_ge(condition, value, expected):
    assert check(condition, value) == expected


@pytest.mark.parametrize("condition,value,expected", [
    ({
        'a__gt': 1
    }, {
        'a': 1
    }, not True),
    ({
        'a__gt': 1
    }, {
        'a': -1
    }, not True),
    ({
        'a__gt': 1
    }, {
        'a': 2
    }, not False),
    ({
        'a__gt': 5
    }, {
        'a': 1.4
    }, not True),
    ({
        'a__gt': 5
    }, {
        'a': 5.1
    }, not False),
    ({
        'a__gt': 1
    }, {
        'a': 0
    }, not True),
])
def test_single_gt(condition, value, expected):
    assert check(condition, value) == expected


@pytest.mark.parametrize("condition,value,expected", [
    ({
        'a__le': 1
    }, {
        'a': 1
    }, True),
    ({
        'a__le': 1
    }, {
        'a': -1
    }, True),
    ({
        'a__le': 1
    }, {
        'a': 2
    }, False),
    ({
        'a__le': 5
    }, {
        'a': 1.4
    }, True),
    ({
        'a__le': 5
    }, {
        'a': 5.1
    }, False),
    ({
        'a__le': 1
    }, {
        'a': 0
    }, True),
])
def test_single_le(condition, value, expected):
    assert check(condition, value) == expected


@pytest.mark.parametrize("condition,value,expected", [
    ({
        'a__eq': 1
    }, {
        'a': 1
    }, True),
    ({
        'a__eq': 1
    }, {
        'a': -1
    }, False),
    ({
        'a__eq': 1
    }, {
        'a': 1.0
    }, True),
    ({
        'a__eq': 1
    }, {
        'a': 1.1
    }, False),
    ({
        'a__eq': 5
    }, {
        'a': 5.1
    }, False),
])
def test_single_eq(condition, value, expected):
    assert check(condition, value) == expected


@pytest.mark.parametrize("condition,value,expected", [
    ({
        'a__ne': 1
    }, {
        'a': 1
    }, not True),
    ({
        'a__ne': 1
    }, {
        'a': -1
    }, not False),
    ({
        'a__ne': 1
    }, {
        'a': 1.0
    }, not True),
    ({
        'a__ne': 1
    }, {
        'a': 1.1
    }, not False),
    ({
        'a__ne': 5
    }, {
        'a': 5.1
    }, not False),
])
def test_single_neq(condition, value, expected):
    assert check(condition, value) == expected


@pytest.mark.parametrize("condition,value,expected", [
    ({
        'a__in': [1, 2, 3]
    }, {
        'a': 1
    }, True),
    ({
        'a__in': [1, 2, 3]
    }, {
        'a': -1
    }, False),
    ({
        'a__in': [1]
    }, {
        'a': 1.0
    }, True),
    ({
        'a__in': [-1.1]
    }, {
        'a': 1.1
    }, False),
])
def test_single_in(condition, value, expected):
    assert check(condition, value) == expected


@pytest.mark.parametrize("condition,value,expected", [
    ({
        'a__nin': [1, 2, 3]
    }, {
        'a': 1
    }, not True),
    ({
        'a__nin': [1, 2, 3]
    }, {
        'a': -1
    }, not False),
    ({
        'a__nin': [1]
    }, {
        'a': 1.0
    }, not True),
    ({
        'a__nin': [-1.1]
    }, {
        'a': 1.1
    }, not False),
])
def test_single_nin(condition, value, expected):
    assert check(condition, value) == expected


@pytest.mark.parametrize("condition,value", [
    ({
        'a__lt': 1
    }, {}),
    ({
        'a__gt': 1
    }, {}),
    ({
        'a__le': 1
    }, {}),
    ({
        'a__ge': 1
    }, {}),
    ({
        'a__eq': 1
    }, {}),
    ({
        'a__ne': 1
    }, {}),
    ({
        'a__in': [1, 2, 3]
    }, {}),
    ({
        'a__nin': [1, 2, 3]
    }, {}),
])
def test_single_op_None(condition, value):
    assert check(condition, value) == True


@pytest.mark.parametrize("condition,value,expected", [
    ({
        'a__lt': 1,
        'a__gt': -1
    }, {
        'a': 0
    }, True),
    ({
        'a__gt': 1,
        'a__lt': 2
    }, {
        'a': 1
    }, False),
    ({
        'a__ge': 1,
        'a__lt': 2
    }, {
        'a': 1
    }, True),
    ({
        'a__ge': 1,
        'a__ne': 2
    }, {
        'a': 2
    }, False),
    ({
        'a__ge': 1,
        'a__ne': 3
    }, {
        'a': 2
    }, True),
])
def test_multiple_op(condition, value, expected):
    assert check(condition, value) == expected


@pytest.mark.parametrize("condition,value", [
    ({
        'n': {
            'a__lt': 1
        }
    }, {}),
    ({
        'n': {
            'a__gt': 1
        }
    }, {}),
    ({
        'n': {
            'a__le': 1
        }
    }, {}),
    ({
        'n': {
            'a__ge': 1
        }
    }, {}),
    ({
        'n': {
            'a__eq': 1
        }
    }, {}),
    ({
        'n': {
            'a__ne': 1
        }
    }, {}),
    ({
        'n': {
            'a__in': [1, 2, 3]
        }
    }, {}),
    ({
        'n': {
            'a__nin': [1, 2, 3]
        }
    }, {}),
])
def test_nested_op_None(condition, value):
    assert check(condition, value) is True


@pytest.mark.parametrize("condition,value,expected", [
    ({
        'n': {
            'a__lt': 1
        }
    }, {
        'n': {
            'a': 1
        }
    }, False),
    ({
        'n': {
            'a__gt': 1
        }
    }, {
        'n': {
            'a': 1
        }
    }, False),
    ({
        'n': {
            'a__le': 1
        }
    }, {
        'n': {
            'a': 2
        }
    }, False),
    ({
        'n': {
            'a__ge': 1
        }
    }, {
        'n': {
            'a': 0
        }
    }, False),
    ({
        'n': {
            'a__eq': 1
        }
    }, {
        'n': {
            'a': 2
        }
    }, False),
    ({
        'n': {
            'a__ne': 1
        }
    }, {
        'n': {
            'a': 1
        }
    }, False),
    ({
        'n': {
            'a__in': [1, 2, 3]
        }
    }, {
        'n': {
            'a': 0
        }
    }, False),
    ({
        'n': {
            'a__nin': [1, 2, 3]
        }
    }, {
        'n': {
            'a': 1
        }
    }, False),
    ({
        'n': {
            'a__lt': 1
        }
    }, {
        'n': {
            'a': 0
        }
    }, True),
    ({
        'n': {
            'a__gt': 1
        }
    }, {
        'n': {
            'a': 2
        }
    }, True),
    ({
        'n': {
            'a__le': 1
        }
    }, {
        'n': {
            'a': 1
        }
    }, True),
    ({
        'n': {
            'a__ge': 1
        }
    }, {
        'n': {
            'a': 1
        }
    }, True),
    ({
        'n': {
            'a__eq': 1
        }
    }, {
        'n': {
            'a': 1
        }
    }, True),
    ({
        'n': {
            'a__ne': 1
        }
    }, {
        'n': {
            'a': 0
        }
    }, True),
    ({
        'n': {
            'a__in': [1, 2, 3]
        }
    }, {
        'n': {
            'a': 1
        }
    }, True),
    ({
        'n': {
            'a__nin': [1, 2, 3]
        }
    }, {
        'n': {
            'a': 4
        }
    }, True),
])
def test_nested_op(condition, value, expected):
    assert check(condition, value) == expected
