swmfpy
======

A collection of tools to make it easier to work with Python and Space Weather Modeling Framework (SWMF) together.

This is a work in progress.

Usage
-----

Clone into the directory you want to use it.

```bash
git clone https://gitlab.umich.edu/qusai/swmfpy.git /path/to/my/dir
```

Then import it into your python project.

```python
import swmfpy
```

Documentation
-------------

Documentation is included as docstrings. Use python's *dir()* and *help()* inbuilt functions to see documentation.

```python
import swmfpy
help(swmfpy)  # To see list of functions
help(swmfpy.io.read_gm_log)  # To see the function documentation
```

An auto-generated markdown document can be found [here](DOCUMENTATION.markdown).
