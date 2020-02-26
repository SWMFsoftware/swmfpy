Contributing
============

Before submitting pull requests please make sure your code complies with the following.

Coding Style: PEP 8
-------------------

The style for your code must follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide. It would be helpful to use a linter like [pylint](https://pylint.org) to check whether your code is complying before submitting.

```bash
pylint somefile.py
```

Coding Standard
---------------

Please write readable code. Make sure your function names well describes your functions. Always include docstrings that use the [Google coding style](http://google.github.io/styleguide/pyguide.html#381-docstrings). The Google coding style guide is a good document to follow so I recommend reading it.

Dependencies
------------

If your code has dependencies that is large and uncommon (e.g. SpacePy) then please seperate it as it's own module. For example you may create a folder:

```bash
mkdir swmfpy/spacepy
touch swmfpy/__init__.py
```

Then your functions will be in swmfpy.spacepy which has its own namespace.

Modules
-------

If you want to create a new module make sure what you're trying to do can't just fit in the modules already made.
