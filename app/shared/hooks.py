from collections.abc import Callable
from typing import Any

PATCH_HOOKS: dict[str, Callable[..., Any]] = {}

_listeners: dict[str, list[Callable]] = {}

def on(event_name: str):
    def decorator(func):
        _listeners.setdefault(event_name, []).append(func)
        return func
    return decorator

def emit(event_name: str, **kwargs):
    for listener in _listeners.get(event_name, []):
        listener(**kwargs)

# so we can do like:
# @on("task.patched")
# def recalculate_progress(session, current_user, **_):
#    tasks_service = create_tasks_service(session, current_user.id, current_user.timezone)
#    return tasks_service.calculate_tasks_progress_today()

def register_patch_hook(
    subtype: str,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        PATCH_HOOKS[subtype] = func
        return func

    return decorator
