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
    if verbose:
        print('Collecting parameters')

    ## collect the geometry parameters
    geometry_params = {
        'kind':geometry
    }
    geometry_params.update(kwargs)

    ## assign defaults for shell
    if verbose:
        print('Adding defaults')
    if 'shell' in geometry_params['kind']:
        geometry_params['center'] = geometry_params.get('center',(0.0,0.0,0.0))
        geometry_params['npolar'] = geometry_params.get('npolar',181)
        geometry_params['nazimuth'] = geometry_params.get('nazimuth',359)

    ## check that we support the geometry
    geometry_param_names = {
        'shell':('radius',)
        ,'line':('r1','r2','npoints')
        ,'rectprism':('center','halfwidth','npoints')
        ,'trajectory':('trajectory_data','trajectory_format')
    }
    if geometry_params['kind'] not in geometry_param_names:
        raise ValueError(f'Geometry {geometry_params["kind"]} not supported!')

    ## check that we've gotten the right /required/ geometry arguments
    for param in geometry_param_names[geometry_params['kind']]:
        if param not in geometry_params:
            raise TypeError(
                f'Geometry {geometry_params["kind"]} '
                f'requires argument {param}!')

    ## check that we support the file type to save as
    file_types = (
        'hdf5'
        ,'pandas_ascii'
        ,'pandas_hdf5'
        ,'tecplot_ascii'
        ,'tecplot_plt'
    )
    if write_as not in file_types:
        raise ValueError(f'File type {write_as} not supported!')

    ## describe the interpolation we're about to do on the data
    if verbose:
        print('Geometry to be interpolated:')
        for key,value in geometry_params.items():
            print(f'\t{key}: {value.__repr__()}')

    ## check whether we are using equations
    ## check that the equations file is there
    use_equations = not (tecplot_equation_file_path is None)
    if use_equations:
        f = open(tecplot_equation_file_path,'r')
        f.close()
        if verbose:
            print('Applying equations from file:')
            print(tecplot_equation_file_path)
    else:
        if verbose:
            print('Not applying any equations')

    ## check patterns
    if not (tecplot_variable_pattern is None) and verbose:
        print(f'Applying pattern {tecplot_variable_pattern} to variables')

    ## check that the tecplot file is there
    if not os.path.exists(tecplot_plt_file_path):
        raise FileNotFoundError(
            f'Tecplot file does not exist: {tecplot_plt_file_path}')
        
    ## load the tecplot data
    if verbose:
        print('Loading tecplot data')
    batsrus = tecplot.data.load_tecplot(tecplot_plt_file_path)

    ## describe the loaded tecplot data
    if verbose:
        print('Loaded tecplot data with variables:')
        print(batsrus.variable_names)

    ## apply equations
    if verbose:
        print('Applying equations to data')
    tecplot_apply_equations(tecplot_equation_file_path)
    if verbose:
        print('Variables after equations:')
        print(batsrus.variable_names)

    ## create geometry zone
    if 'shell' in geometry_params['kind']:
        geometry_points = shell_geometry(geometry_params)
    elif 'line' in geometry_params['kind']:
        geometry_points = line_geometry(geometry_params)
    elif 'rectprism' in geometry_params['kind']:
        geometry_points = rectprism_geometry(geometry_params)
    elif 'trajectory' in geometry_params['kind']:
        geometry_points = trajectory_geometry(geometry_params)

    source_zone = list(batsrus.zones())
    new_zone = batsrus.add_ordered_zone('geometry',geometry_points['npoints'])
    for i,d in zip((0,1,2),('X','Y','Z')):
        new_zone.values(i)[:] = geometry_points[d][:]
        
    ## interpolate variables on to the geometry
    if verbose:
        print('Interpolating variables:')
    variables = list(batsrus.variables(re.compile(tecplot_variable_pattern)))
    if verbose:
        for var in variables:
            print(var.name)
    tecplot.data.operate.interpolate_linear(
        destination_zone=new_zone
        ,source_zones=source_zone
        ,variables=variables
    )
    ## add variables for shell and trajectory cases
    if 'shell' in  geometry_params['kind']:
        batsrus.add_variable('polar')
        new_zone.values('polar')[:] = geometry_points['polar']
        batsrus.add_variable('azimuthal')
        new_zone.values('azimuthal')[:] = geometry_points['azimuthal']
    if 'trajectory' in geometry_params['kind']:
        batsrus.add_variable('time')
        new_zone.values('time')[:] = geometry_points['time']

    ## add auxiliary data
    new_zone.aux_data.update(geometry_params)
    if ('trajectory' in geometry_params['kind']
        and 'pandas' in geometry_params['trajectory_format']):
        new_zone.aux_data.update(
            {'trajectory_data': type(geometry_params['trajectory_data'])}
        )

    ## construct default filename
    if filename == None:
        filename = tecplot_plt_file_path[:-4] + f'_{geometry_params["kind"]}'
    
    ## save zone
    if verbose:
        print(f'Writing {filename}')
    if 'hdf5' in write_as:
        save_hdf5()
    elif 'pandas_ascii' in write_as:
        save_pandas_ascii(filename,batsrus,variables)
    elif 'pandas_hdf5' in write_as:
        save_pandas_hdf5()
    elif 'tecplot_ascii' in write_as:
        tecplot.data.save_tecplot_ascii(
            filename
            ,zones=new_zone
            ,use_point_format='True'
        )
    elif 'tecplot_plt' in write_as:
        tecplot.data.save_tecplot_plt(
            filename
            ,zones=new_zone
        )
