from .config import output_config

def verbosity_required(level=1):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            if output_config.quiet or output_config.verbosity < level:
                return
            return fn(*args, **kwargs)
        return wrapper
    return decorator
