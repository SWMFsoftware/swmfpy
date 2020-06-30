#!/usr/bin/env python
"""Tools for working with the Tecplot visualization software.

Requires an active Tecplot license and the pytecplot python package.
pytecplot ships with Tecplot 360 2017 R1 and later versions
but it is recommended that you install the latest version with
`pip install pytecplot`.
See the pytecplot documentation for more details about
[installation](https://www.tecplot.com/docs/pytecplot/install.html).
See also [TECPLOT](TECPLOT.markdown) for tips targeted to SWMF users.

Some useful references:
- [Tecplot User's Manual](download.tecplot.com/360/current/360_users_manual.pdf)
- [Tecplot Scripting Guide](download.tecplot.com/360/current/360_scripting_guide.pdf)
- [Pytecplot documentation](www.tecplot.com/docs/pytecplot/index.html)
"""
__all__ = [
    'apply_equations'
]
__author__ = 'Camilla D. K. Harris'
__email__ = 'cdha@umich.edu'

import numpy as np
import tecplot

def apply_equations(eqn_path: str, verbose: bool = False):
    """Apply an equations file in the Tecplot macro format to the active dataset

    Please reference the Tecplot User's Manual for more details on
    equation files and syntax. It is recommended to use this function with eqn
    files generated with the Tecplot GUI.
    See [TECPLOT](TECPLOT.markdown) for tips on using pytecplot.

    Args:
        eqn_file_path (str): The path to the equation macro file (typically with
            extension `.eqn`).
        verbose (bool): (Optional) Whether or not to print the equations as they
            are applied. Default behavior is silent.

    Examples:
        ```python
        import tecplot
        import swmfpy.tecplottools as tpt

        ## Uncomment this line if you are connecting to a running tecplot
        ## session. Be sure that the port number matches the port the GUI is
        ## listening to. See TECPLOT.markdown for tips on connecting to a
        ## running session or running your script seperately.
        # tecplot.session.connect(port=7600)

        ## load a dataset
        dataset = tecplot.data.load_tecplot('./z=0_mhd_1_n00000000.plt')

        ## apply an equations file
        tpt.apply_equations('./gse_to_ephio.eqn', verbose= True)

        ## apply a frame style
        frame = tecplot.active_frame()
        frame.load_stylesheet('./density.sty')

        ## annotate with the zone name
        frame.add_text('&(ZONENAME[ACTIVEOFFSET=1])', position= (5, 95))

        ## save the image
        tecplot.export.save_png('./density.png', width= 1200, supersample= 8)
        ```
    """
    if verbose:
        print('Executing:')
    with open(eqn_path, 'r') as eqn_file:
        for line in eqn_file:
            if '$!alterdata' in line.lower():
                eqn_line = eqn_file.readline()
                try:
                    eqn_str = eqn_line.split("'")[1]
                except IndexError:
                    try:
                        eqn_str = eqn_line.split("\"")[1]
                    except:
                        raise ValueError(f'Unable to read equation: {eqn_line}')
                tecplot.data.operate.execute_equation(eqn_str)
                if verbose:
                    print(eqn_str)
    if verbose:
        print('Successfully applied equations.')


def _shell_geometry(geometry_params):
    """Returns a dict containing points for the described shell geometry.
    """


def _line_geometry(geometry_params):
    """Returns a dict containing points for the described line geometry.
    """


def _rectprism_geometry(geometry_params):
    """Returns a dict containing points for the described rectprism geometry.
    """


def _trajectory_geometry(geometry_params):
    """Returns a dict containing points for the described trajectory geometry.
    """


def _save_hdf5():
    """Save the aux data and a subset of the variables in hdf5 format.
    """


def _save_ascii():
    """Save the aux data and a subset of the variables in plain-text format.
    """


def tecplot_interpolate(
        tecplot_plt_file_path:str
        ,geometry:str
        ,write_as:str
        ,filename:str=None
        ,tecplot_equation_file_path:str=None
        ,tecplot_variable_pattern:str=None
        ,verbose:bool=False
        ,**kwargs
):
    """Interpolates Tecplot binary data onto various geometries.

    Args:
        tecplot_plt_file_path (str): Path to the tecplot binary file.
        geometry (str): Type of geometry for interpolation. Supported geometries
            are 'shell', 'line', 'rectprism', or 'trajectory'.
        write_as (str): Type of file to write to. Supported options are 'hdf5',
            'ascii', 'tecplot_ascii', and 'tecplot_plt'.
        filename (str): (Optional) Name of the file to write to. Defaults to a
            concatenation of the tecplot file name and the geometry type.
        tecplot_equation_file_path (str): (Optional) Path to an equation file to
            be applied to the tecplot dataset before interpolation. Defaults to
            no equations.
        tecplot_variable_pattern (str): (Optional) Regex-style variable name
            pattern used to save a subset of the variables. This option may be
            used to decrease the size of the hdf5 output. Default behavior is to
            save all variables.
        verbose: (Optional) Print diagnostic information. Defaults to False.

    Keyword Args:
        center (array-like): Argument for the 'shell' geometry. Contains the X,
            Y, and Z positions of the shell. Defaults to (0,0,0).
        radius (float): Argument for the 'shell' geometry. Required.
        npoints (array-like): Argument for the 'shell' geometry. Contains the
            number of points in the azimuthal and polar directions to
            interpolate onto. Defaults to (359,181).
        r1 (array-like): Argument for the 'line' geometry. Contains the X, Y,
            and Z positions of the point where the line starts. Required.
        r2 (array-like): Argument for the 'line' geometry. Contains the X, Y,
            and Z positions of the point where the line ends. Required.
        npoints (int): Argument for the 'line' geometry. The number of points
            along the line to interpolate onto. Required.
        center (array-like): Argument for the 'rectprism' geometry. Contains the
            X, Y, and Z positions of the center of the rectangular prism.
            Defaults to (0,0,0).
        halfwidth (array-like): Argument for the 'rectprism' geometry. Contains
            the half widths of the rectangular prism in the X, Y, and Z
            directions. Required.
        npoints (array-like): Argument for the 'rectprism' geometry. Contains
            the number of points in the X, Y, and Z directions to interpolate
            onto. Required.
        trajectory_data (str): Argument for the 'trajectory' geometry. The path
            to the ASCII trajectory data file. Required.
        trajectory_format (str): Argument for the 'trajectory' geometry. The
            format of the trajectory data file. Supported formats are 'tecplot'
            (data is a tecplot zone with 3D positional variables and 'time') and
            'batsrus' (data is formatted as described for the #SATELLITE
            command, see SWMF documentation). Required.

    Examples:
        ```tecplot_interpolate(
            tecplot_plt_file_path='./path/to/data.plt'
            ,geometry='shell'
            ,write_as='tecplot_ascii'
            ,center=[0.0, 0.0, 0.0]
            ,radius=1.01
        )

        tecplot_interpolate(
            tecplot_plt_file_path='./path/to/data.plt'
            ,geometry='line'
            ,write_as='tecplot_ascii'
            ,tecplot_equation_file_path='./path/to/equations.eqn'
            ,tecplot_variable_pattern='B.*|E.*'
            ,r1=[1.0, 0.0, 0.0]
            ,r2=[6.0, 0.0, 0.0]
            ,npoints=101
        )
        ```
    """
