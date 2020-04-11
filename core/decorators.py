

def handle_exceptions(func):
    try:
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
        
        return wrapper
    except Exception as e:
        return