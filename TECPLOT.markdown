# author: Camilla D. K. Harris
# email: cdha@umich.edu

Visualization of SWMF output with Tecplot
=========================================
To be completed.

Generating Tecplot-readable output
----------------------------------
- summary of tecplot functionality in #SAVEPLOT command
- use of #SAVETECPLOT and #SAVETECPLOTBINARY commands
- brief note on szplt file type, how to create them, and the szplt server tool
  for HPC/linux systems

Using pytecplot
---------------
The pytecplot documentation can be found at
https://www.tecplot.com/docs/pytecplot/. Tecplot and pytecplot require a valid
Tecplot 360 license to use.

The latest version of pytecplot can be installed with `pip install pytecplot`.
Linux and Windows users should consult the appropriate sections of the
pytecplot documentation (https://www.tecplot.com/docs/pytecplot/install.html)
for further details; the rest of this section pertains to MacOS users.

MacOS users running python scripts which use pytecplot can connect to the
Tecplot engine either through a running instance of the Tecplot GUI or
automatically by setting the appropriate environment variable.

To connect a script to a running instance of Tecplot, open the Tecplot GUI.
Select `Scripting > PyTecplot Connections...` from the drop-down menus to open
the PyTecplot Connections dialog. Then tick the box to `Accept connections` from
the port number of your choice. Then in your python script add the following
line immediately after your import statements:
```python
import tecplot

tecplot.session.connect(port=7600)

...
```
Be sure that the port numbers match.
In the command line you will be able to run your script:
```bash
python my_pytecplot_script.py
```
And the effects will be mirrored in the GUI.

To run a script without connecting to a running instance of Tecplot requires
setting the `DYLD_LIBRARY_PATH` environment variable so that it references the
Tecplot libraries. However, it is not recommended to set this variable
permanently as this will cause severe conflicts with other applications. Tecplot
provides their own recommendations for temporarily setting the environment
variable (https://www.tecplot.com/docs/pytecplot/install.html#id22) but a simple
solution is as follows:

Add the following line to your `.bash_profile` or `.bashrc` file:
```bash
alias runpytecplot='env DYLD_LIBRARY_PATH="/Applications/Tecplot 360 EX 2019 R1/Tecplot 360 EX 2019 R1.app/Contents/MacOS/"'
```
Be sure to replace `2019 R1` with the appropriate version and check that the
path is valid on your system. Then your script can be run like so:
```bash
runpytecplot python my_pytecplot_script.py
```