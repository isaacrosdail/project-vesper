import pytest
from app.modules.tasks.validators import *


@pytest.mark.parametrize("name, expected", [
    ("Task 1", []),
    ("", [TASK_NAME_REQUIRED]),
    ("a" * 151, [TASK_NAME_TOO_LONG]),
])
def test_validate_task_name(name, expected):
    assert validate_task_name(name) == expected


@pytest.mark.parametrize("priority, expected", [
    ("HIGH", []),
    ("", [PRIORITY_REQUIRED]),
    ("not_a_priority", [PRIORITY_INVALID]),
])
def test_validate_task_priority(priority, expected):
    assert validate_task_priority(priority) == expected


@pytest.mark.skip(reason="Due_date validation not implemented yet")
def test_validate_due_date(): ...


@pytest.mark.parametrize("data, expected", [
    ({"name": "work"}, []),
    ({"name": "a" * 51}, [TAG_NAME_LENGTH]),
    ({"scope": "a" * 21}, [TAG_NAME_REQUIRED, TAG_SCOPE_LENGTH]),
    ({}, [TAG_NAME_REQUIRED]),
    ({"name": "home", "scope": "a" * 21}, [TAG_SCOPE_LENGTH]),
])
def test_validate_tag(data, expected):
    assert validate_tag(data) == expected