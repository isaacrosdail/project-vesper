
import pytest
import datetime
from app.modules.tasks.validators import *


@pytest.mark.parametrize("task_name, expected_value, expected_errors", [
    ("Task 1", "Task 1", []),
    ("", None, [TASK_NAME_REQUIRED]),
    ("a" * 151, None, [TASK_NAME_TOO_LONG]),
])
def test_validate_task_name(task_name, expected_value, expected_errors):
    typed_value, errors = validate_task_name(task_name)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("priority, expected_value, expected_errors", [
    ("HIGH", PriorityEnum.HIGH, []),
    ("", None, []), # Optional at field-level, existence enforced in validate_task
    ("not_a_priority", None, [PRIORITY_INVALID]),
])
def test_validate_task_priority(priority, expected_value, expected_errors):
    typed_value, errors = validate_task_priority(priority)
    assert typed_value == expected_value
    assert errors == expected_errors



@pytest.mark.parametrize("data, expected_typed_data, expected_errors", [
    pytest.param(
        {"name": "Walk dog", "priority": "MEDIUM"},
        {"name": "Walk dog", "priority": PriorityEnum.MEDIUM},
        {},
        id="valid-non-frog-task"
    ),
    pytest.param(
        {"name": "Eat", "is_frog": True, "due_date": "2025-10-04"},
        {"name": "Eat", "is_frog": True, "due_date": datetime.date(2025, 10, 4)},
        {},
        id="valid-frog-task"
    ),
    pytest.param(
        {"name": "Dust shelves"},
        {"name": "Dust shelves"},
        {
            "priority": [PRIORITY_REQUIRED_NON_FROG]
        },
        id="non-frog-priority-required"
    ),
    pytest.param(
        {"name": "Make bed", "is_frog": True, "priority": None},
        {"name": "Make bed", "is_frog": True},
        {
            "due_date": [FROG_REQUIRES_DUE_DATE]
        },
        id="frog-requires-due-date"
    ),
    pytest.param(
        {"name": "Grab snacks", "is_frog": True, "due_date": "2025-09-28", "priority": "HIGH"},
        {"name": "Grab snacks", "is_frog": True, "due_date": datetime.date(2025, 9, 28), "priority": PriorityEnum.HIGH},
        {
            "priority": [FROG_REQUIRES_NO_PRIORITY]
        },
        id="frog-priority-must-be-none"
    ),
])
def test_validate_task(data, expected_typed_data, expected_errors):
    typed_data, errors = validate_task(data)
    assert typed_data == expected_typed_data
    assert errors == expected_errors



@pytest.mark.parametrize("tag_name, expected_value, expected_errors", [
    ("MyTag", "MyTag", []),
    ("TagTooLong" * 10, None, [TAG_NAME_LENGTH]),
])
def test_validate_tag_name(tag_name, expected_value, expected_errors):
    typed_value, errors = validate_tag_name(tag_name)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("tag_scope, expected_value, expected_errors", [
    ("MyTag", "MyTag", []),
    ("TagTooLong" * 10, None, [TAG_SCOPE_LENGTH]),
])
def test_validate_tag_scope(tag_scope, expected_value, expected_errors):
    typed_value, errors = validate_tag_scope(tag_scope)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("data, expected_typed_data, expected_errors", [
    pytest.param(
        {"name": "work"},
        {"name": "work"},
        {},
        id="valid-name"
    ),
    pytest.param(
        {"name": "a" * 51},
        {},
        {"name": [TAG_NAME_LENGTH]},
        id="name-too-long"
    ),
    pytest.param(
        {"scope": "a" * 21},
        {},
        {"name": [TAG_NAME_REQUIRED], "scope": [TAG_SCOPE_LENGTH]},
        id="missing-name+scope-too-long"
    ),
    pytest.param(
        {},
        {},
        {"name": [TAG_NAME_REQUIRED]},
        id="missing-name"
    ),
    pytest.param(
        {"name": "home", "scope": "a" * 21},
        {"name": "home"},
        {"scope": [TAG_SCOPE_LENGTH]},
        id="valid-name+scope-too-long"
    ),
])
def test_validate_tag(data, expected_typed_data, expected_errors):
    typed_data, errors = validate_tag(data)
    assert typed_data == expected_typed_data
    assert errors == expected_errors