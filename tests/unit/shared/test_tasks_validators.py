import pytest
from app.modules.tasks.validators import validate_task, validate_tag
from app.modules.tasks.models import Priority

# Task constants
TASK_NAME_REQUIRED = "Task name is required"
TASK_NAME_LENGTH = "Task name must be under 255 characters"
PRIORITY_INVALID = "Invalid priority"

# Tag constants  
TAG_NAME_REQUIRED = "Tag name is required"
TAG_NAME_LENGTH = "Tag name must be under 50 characters"
TAG_SCOPE_LENGTH = "Tag scope must be under 20 characters"

@pytest.mark.parametrize("task_data", [
    {"name": "Buy groceries"},
    {"name": "Important task", "priority": "high"},
    {"name": "a" * 255},
    # All priorities
    {"name": "Low priority task", "priority": "low"},
    {"name": "Medium priority task", "priority": "medium"},
])
def test_validate_task_success(task_data):
    assert validate_task(task_data) == []

@pytest.mark.parametrize("task_data,expected_errors", [
    # Missing name
    ({"priority": "high"}, [TASK_NAME_REQUIRED]),
    ({}, [TASK_NAME_REQUIRED]),
    
    # Name too long
    ({"name": "a" * 256}, [TASK_NAME_LENGTH]),
    
    # Invalid priority
    ({"name": "Task", "priority": "invalid_priority"}, [PRIORITY_INVALID]),
])
def test_validate_task_errors(task_data, expected_errors):
    errors = validate_task(task_data)
    for expected_error in expected_errors:
        assert expected_error in errors

@pytest.mark.parametrize("tag_data", [
    # Basic valid tag
    {"name": "work"},
    # With scope
    {"name": "personal", "scope": "user"},
    # Max lengths
    {"name": "a" * 50, "scope": "b" * 20},
])
def test_validate_tag_success(tag_data):
    assert validate_tag(tag_data) == []

@pytest.mark.parametrize("tag_data,expected_errors", [
    # Missing name
    ({}, [TAG_NAME_REQUIRED]),
    ({"scope": "user"}, [TAG_NAME_REQUIRED]),
    
    # Name too long
    ({"name": "a" * 51}, [TAG_NAME_LENGTH]),
    
    # Scope too long
    ({"name": "work", "scope": "a" * 21}, [TAG_SCOPE_LENGTH]),
])
def test_validate_tag_errors(tag_data, expected_errors):
    errors = validate_tag(tag_data)
    for expected_error in expected_errors:
        assert expected_error in errors