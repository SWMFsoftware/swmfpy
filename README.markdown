swmfpy
======

A collection of tools to make it easier to work with Python and Space Weather Modeling Framework (SWMF) together.

This is a work in progress.

Usage
-----

Clone into the directory you want to use it (swmfpy also is part of the SWMF and gets cloned into SWMF/share/Python)

```bash
git clone https://gitlab.umich.edu/swmf_sofware/swmfpy.git /path/to/my/dir
```

Set the PYTHONPATH environment variable to include this directory. Then import it into your python project. 

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

However if you would like an auto-documented version (uses exact same text as the help() function output), go [here](DOCUMENTATION.markdown).
