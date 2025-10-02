
import pytest

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
    ("", None, [PRIORITY_REQUIRED]),
    ("not_a_priority", None, [PRIORITY_INVALID]),
])
def test_validate_task_priority(priority, expected_value, expected_errors):
    typed_value, errors = validate_task_priority(priority)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.skip(reason="Due_date validation not implemented yet")
def test_validate_due_date(): ...


@pytest.mark.parametrize("data, expected_typed_data, expected_errors", [
    pytest.param(
        {"name": "Implement due_date validation", "priority": "MEDIUM"},
        {"name": "Implement due_date validation", "priority": PriorityEnum.MEDIUM},
        {},
        id="valid-name-priority"
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