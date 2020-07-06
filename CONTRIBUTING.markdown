Contributing
============

Before submitting pull requests please make sure your code complies with the following.

Git etiquette
-------------

If you're planning on adding a feature (new function or class) then create your own branch,

```shell
$ git checkout -b my_new_feature
```

and start commiting there to test and work on. We will follow a [trunk-based development model](https://youtu.be/ykZbBD-CmP8). This means we will rapidly merge branches once you have something stable and continue with master branch. So make sure to push something stable instead of being in your feature branch for too long. I will try to address your pull request ASAP.

[![Trunk-based Development](http://img.youtube.com/vi/ykZbBD-CmP8/0.jpg)](https://www.youtube.com/watch?v=ykZbBD-CmP8 "Trunk-based Development")

Coding Style: PEP 8
-------------------

The style for your code must follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide. It would be helpful to use a linter like [pylint](https://pylint.org) to check whether your code is complying before submitting.

```shell
$ pylint somefile.py
```

Coding Standard
---------------

Please write readable code. Make sure your function names well describes your functions. Always include docstrings that use the [Google coding style](http://google.github.io/styleguide/pyguide.html#381-docstrings). The Google coding style guide is a good document to follow so I recommend reading it.

Metadata
--------

Include metadata if you made a new function or module. Name and email will suffice. Use the variable names `__author__` and `__email__` for modules and comments for functions that you add to someone else's module. For example:

mynewpackage.py:

```python
"""A new package for swmfpy
"""
__all__ = ['funcs', 'to', 'export']
__author__ = 'Rita Hayworth'
__email__ = 'rita@umich.edu'
```

Or for a function:
```python
def my_new_func(some_args):
    """my docstring
    """
    # Author: Diane Selwyn
    # Email:  diane@umich.edu

    # function body
```

Dependencies
------------

If your code has dependencies that is large and uncommon (e.g. SpacePy) then please import it in the function and be explicit about the dependencies. For example you may create a function:

```python
def func_with_dependency():
	"""Func does this.

	Depends on spacepy. Try `pip install -U spacepy`
	"""
	import spacepy
	# Function body
```

Then your functions will be in swmfpy.spacepy which has its own namespace.

Modules
-------

If you want to create a new module make sure what you're trying to do can't just fit in the modules already made.
