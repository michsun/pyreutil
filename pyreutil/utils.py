import functools
import os

from typing import Callable, List

# TODO: Decorator type hints????? 
# TODO: Improve clarity when initialising objects
def mutually_exclusive(keyword, *keywords):
    """Decorator raises a TypeError if input function arguments are not mutually exclusive."""
    keywords = (keyword,)+keywords
    def _wrapper(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            if sum(k in keywords for k in kwargs) != 1:
                raise TypeError('You must specify exactly one of {}'.format(', '.join(keywords)))
            return func(*args, **kwargs)
        return inner
    return _wrapper