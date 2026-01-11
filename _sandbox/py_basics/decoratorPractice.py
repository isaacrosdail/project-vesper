
def requires_role(role: UserRoleEnum) -> Callable[..., Any]:
    def decorator(f: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            if not current_user.has_role(role):
                return abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator