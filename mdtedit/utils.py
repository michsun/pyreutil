import functools
import os
import time

from typing import Callable, List

def colored(r: int, g: int, b: int, text: str) -> str:
    """Returns a colored version of the string."""
    # return "\033[38;2;{};{};{}m{}\033[38;2;255;255;255m".format(r, g, b, text)
    return "\033[38;2;{};{};{}m{}\033[m".format(r, g, b, text)

# TODO: Decorator type hints????? 
def mutually_exclusive(keyword, *keywords):
    keywords = (keyword,)+keywords
    def _wrapper(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            if sum(k in keywords for k in kwargs) != 1:
                raise TypeError('You must specify exactly one of {}'.format(', '.join(keywords)))
            return func(*args, **kwargs)
        return inner
    return _wrapper

def timer(function_without_args=None, *args, **kwargs):
    """Decorator function that times the functions."""
    # print(type(func_no_args), len(args), len(kwargs))
    precision = {
        's': 1,
        'ms': 1000,
    }
    # Default args
    unit = 'ms'
    rnd = 0
    
    def _decorate(func):
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            diff = (end-start) * precision[unit]
            if rnd:
                diff = round(diff,rnd)
            print(f'\'{func.__name__}\' finished in {diff} {unit}')
            return result
        return wrapper
    
    if function_without_args:
        return _decorate(function_without_args)
    
    if 'unit' in kwargs:
        unit = kwargs['unit']
    if 'round' in kwargs:
        rnd = kwargs['round']
    
    return _decorate