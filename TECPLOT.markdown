author: Camilla D. K. Harris

email: cdha@umich.edu

Visualization of SWMF output with Tecplot
=========================================
To be completed.

Generating Tecplot-readable output
----------------------------------
- summary of tecplot functionality in #SAVEPLOT command
- use of #SAVETECPLOT and #SAVETECPLOTBINARY commands

Using pytecplot
---------------
Tecplot and pytecplot require a valid Tecplot 360 license to use. Please
consult the [pytecplot documentation](https://www.tecplot.com/docs/pytecplot/)
for the most definitive and up-to-date information.

The latest version of pytecplot can be installed with `pip install pytecplot`.
Linux and Windows users should consult the installation sections of the
[pytecplot documentation](https://www.tecplot.com/docs/pytecplot/install.html)
for further details; the rest of this section pertains to MacOS users.

MacOS users running python scripts which use pytecplot can connect to the
Tecplot engine either through a running instance of the Tecplot GUI or
automatically in "batch" mode by setting the appropriate environment variable.

### Connect a python script to a running instance of Tecplot

To connect a script to a running instance of Tecplot, open the Tecplot GUI.
Select *Scripting > PyTecplot Connections...* from the drop-down menus to open
the **PyTecplot Connections** dialog. Then tick the box to 
**Accept connections** from the port number of your choice. Then in your python
script add the following line immediately after your import statements:
```python
import tecplot

tecplot.session.connect(port=7600)

...
```
Be sure that the port numbers match.
In the terminal you will be able to run your script:
```bash
python my_pytecplot_script.py
```
And the effects will be mirrored in the GUI.

### Run a python script in batch mode

To run a script without connecting to a running instance of Tecplot requires
setting the `DYLD_LIBRARY_PATH` environment variable so that it references the
Tecplot libraries. However, it is not recommended to set this variable
permanently as this will cause severe conflicts with other applications.
Tecplot provides their own [recommendations for temporarily setting the
environment variable](https://www.tecplot.com/docs/pytecplot/install.html#id22)
but a simple solution is as follows:

Add the following line to your `.bash_profile` or `.bashrc` file:
```bash
alias runpytecplot='env DYLD_LIBRARY_PATH="/Applications/Tecplot 360 EX 2019 R1/Tecplot 360 EX 2019 R1.app/Contents/MacOS/"'
```
Be sure to replace `2019 R1` with the appropriate version and check that the
path is valid on your system. Use `source` with your bash profile to make the
alias available to your environment. Then your script can be run from the
terminal like so:
```bash
runpytecplot python my_pytecplot_script.py
```

The SZL file format
------------------
Tecplot can show and manipulate data that is stored on a remote machine such as
NASA Pleiades from the GUI on your university desktop. There are a few
limitations and caveats:

- The remote machine should use a linux operating system (as do most
  supercomputers) and have Tecplot installed.
- The remote machine should have the `szlserver` tool installed (this ships
  with Tecplot and can be installed in the user’s home directory). See
  Tecplot's [advice regarding szlserver](https://www.tecplot.com/products/szl-server/).
- The remote data must be in the SZL file format (files can be converted easily
  with tecplot’s batch processing command line tool).

After the initial set up there are a couple extra steps, but once remote data
is loaded it can be manipulated and inspected in the Tecplot GUI just as if the
data was stored on the client computer. SWMF users may find this useful for
inspecting simulations in progress before committing to a possibly lengthy
download.

### Setting up

#### Install szlserver

Log in to the remote machine and run the installation script provided by
Tecplot.
```bash
bash /path/to/tecplot/2019r1/360ex_2019r1/szlserver/tecplotszlserver2019r1_linux64.sh
```
The path will certainly change as new versions of Tecplot are released, so be
sure to check that the path is valid and up to date. Bear in mind that you may
need to load a Tecplot module to access the software; consult the remote
system's user guide or software documentation.

On most HPC systems you will not have root privileges, so follow the prompts to
install the tool in your home directory. Afterwards you will need to add the
tool to your path; in bash you can do this by adding the following line to your
bash profile:
```bash
PATH=$PATH:$HOME/tecplotszlserver2019r1/bin
```
Again, be sure the version and path is correct. Afterwards use `source` and try
`which szlserver` to be sure that the tool is installed and on your system's
path.

#### Convert data to SZL file format

On the remote machine navigate to the directory where your data is located. Try
`which tec360` to be sure that the Tecplot batch processing tool is installed.
If it is not installed see the [Tecplot User's Guide](http://download.tecplot.com/360/current/360_users_manual.pdf)
for details on batch processing.

Run the following command to convert a single file to SZL format:
```bash
tec360 z=0_mhd.plt -o output.szplt
```

If your simulation results span many `.plt` files (multiple time steps, or
multiple iterations) you can combine the multiple zones into one SZL file.
```bash
tec360 z=0_mhd_*.plt -o output.szplt
```

### Loading remote data

On your desktop, open the Tecplot GUI. Select *File > Load Remote Data...* from
the drop-down menus to open the **Remote Data Load Options** dialog. Select 
**Manual Connection** and from there select **Connect**. This will open the 
**Waiting for Server Connection** dialog.

The dialog will provide you with a command that will look something like:
```bash
szlserver -m ???.???.???.??? -p ????? -k ?????????
```

Log into the remote machine and run the command that Tecplot provided.

Once the connection is established, the **Waiting...** dialog on your local
machine should close and the **Remote...** dialog should permit you to select
data from the remote machine. Find the SZL data and load it.

From here the remote data can be manipulated in the GUI and plots can be
exported on your local machine.