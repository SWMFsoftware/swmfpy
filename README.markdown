![swmfpy logo](share/logo/swmfpy.png "swmfpy")

swmfpy
======

A collection of tools to make it easier to work with Python and Space Weather Modeling Framework (SWMF) together.

This is a work in progress.

Usage
-----

*Note*: swmfpy also is part of the SWMF and gets cloned into `SWMF/share/Python`. If you ran `Config.pl -install` while installing SWMF you probably already have it installed in your Python distribution. If you have already done this it is installed on your system. However, if you would like to [develop](CONTRIBUTING.markdown) for swmfpy or have a local copy continue reading.

Clone into the directory you want to use it.

```bash
git clone https://gitlab.umich.edu/swmf_sofware/swmfpy.git /path/to/my/dir
```

Then go to its directory and run `setup.py` make sure to include `--user`.

```bash
cd /path/to/swmfpy
python3 -m pip install setuptools wheel twine --user # If you don't have these
python3 setup.py install --user
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

However if you would like an auto-documented version (uses exact same text as the help() function output), go [here](DOCUMENTATION.markdown).

*Note*: The autodoc tool has troubles escaping the `#` symbol so examples with `#COMMAND`s in `PARAM.in` files will not show the symbol. Perhaps I can find a fix but the `help()` pages are always better and up to date.

Issues
------

If you are experiencing any issues or bugs please go to the [Issues](https://gitlab.umich.edu/swmf_software/swmfpy/issues) page and create an issue. Make sure you include steps to recreate the problem in your post.
