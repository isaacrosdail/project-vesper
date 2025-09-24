import pytest
from app.modules.tasks.validators import *


@pytest.mark.parametrize("task_data", [
    {"name": "Buy groceries"},
    {"name": "Important task", "priority": "high"},
    {"name": "a" * 255},
    {"name": "Low priority task", "priority": "low"},
    {"name": "Medium priority task", "priority": "medium"},
])
def test_validate_task_success(task_data):
    assert validate_task(task_data) == []

@pytest.mark.parametrize("task_data,expected_errors", [
    ({"priority": "high"}, [TASK_NAME_REQUIRED]),
    ({}, [TASK_NAME_REQUIRED]),
    ({"name": "a" * 256}, [TASK_NAME_LENGTH]),
    ({"name": "Task", "priority": "invalid_priority"}, [PRIORITY_INVALID]),
])
def test_validate_task_errors(task_data, expected_errors):
    errors = validate_task(task_data)
    assert set(errors) == set(expected_errors)

@pytest.mark.parametrize("tag_data", [
    {"name": "work"},
    {"name": "personal", "scope": "global"},
    {"name": "a" * 50, "scope": "b" * 20},
    {"name": "urgent"},
])
def test_validate_tag_success(tag_data):
    assert validate_tag(tag_data) == []

@pytest.mark.parametrize("tag_data,expected_errors", [
    ({}, [TAG_NAME_REQUIRED]),
    ({"scope": "user"}, [TAG_NAME_REQUIRED]),
    ({"name": "a" * 51}, [TAG_NAME_LENGTH]),
    ({"name": "work", "scope": "a" * 21}, [TAG_SCOPE_LENGTH]),
])
def test_validate_tag_errors(tag_data, expected_errors):
    errors = validate_tag(tag_data)
    assert set(errors) == set(expected_errors)