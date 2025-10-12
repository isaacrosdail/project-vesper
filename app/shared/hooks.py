
PATCH_HOOKS = {}

def register_patch_hook(subtype):
    def decorator(func):
        PATCH_HOOKS[subtype] = func
        return func
    return decorator
