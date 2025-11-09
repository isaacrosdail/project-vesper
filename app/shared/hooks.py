
from typing import Callable, Any

PATCH_HOOKS: dict[str, Callable[..., Any]] = {}

def register_patch_hook(subtype: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        PATCH_HOOKS[subtype] = func
        return func
    return decorator
