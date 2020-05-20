![swmfpy logo](share/logo/swmfpy.png "swmfpy")

swmfpy
======

A collection of tools to make it easier to work with Python and Space Weather Modeling Framework (SWMF) together.

This is a work in progress.

Installation
------------

Clone into the directory you want to use it.

*Note*: swmfpy also is part of the SWMF and gets cloned into `SWMF/share/Python`. However, if you would like to [develop](CONTRIBUTING.markdown) for swmfpy or have a local copy do the following:

```bash
# Skip this if using it in SWMF directory.
git clone https://gitlab.umich.edu/swmf_sofware/swmfpy.git /path/to/my/dir
```

Then go to its directory and run [pip](https://pip.pypa.io/en/stable/) to install. Make sure to include `--user`.

```bash
cd SWMF/share/Python  # or your clone directory
pip install --user .
```

*Note*: Depending on your system [pip](https://pip.pypa.io/en/stable/) may be ran in several ways: `pip`, `pip3`, or `python3 -m pip`

Then import it into your python project. 

```python
import swmfpy
```

Documentation
-------------

An auto-documented version can be found [here](DOCUMENTATION.markdown).

However, documentation is included as docstrings. Use python's *dir()* and *help()* inbuilt functions to see documentation.

```python
import swmfpy
help(swmfpy)  # To see list of functions
help(swmfpy.io.read_gm_log)  # To see the function documentation
```

Issues
------

If you are experiencing any issues or bugs please go to the [Issues](https://gitlab.umich.edu/swmf_software/swmfpy/issues) page and create an issue. Make sure you include steps to recreate the problem in your post.
