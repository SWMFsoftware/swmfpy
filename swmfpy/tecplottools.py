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
    'apply_equations',
    'tecplot_interpolate'
]
__author__ = 'Camilla D. K. Harris'
__email__ = 'cdha@umich.edu'

import os
import re

import h5py
import numpy as np
import tecplot

def apply_equations(eqn_path: str, verbose: bool = False) -> None:
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


def _shell_geometry(geometry_params: dict) -> dict:
    """Returns a dict containing points for the described shell geometry.
    """
    nlon = geometry_params['npoints'][0] # 360
    nlat = geometry_params['npoints'][1] # 179
    lons = np.linspace(0, 360, nlon, endpoint=False)
    dlat = 180/(nlat + 1)
    lats = np.linspace(-90.0+dlat, 90.0-dlat, nlat)
    print(f'lons: {lons}')
    print(f'lats: {lats}')

    latvals, lonvals = np.meshgrid(lats, lons)
    phvals = np.deg2rad(-1*lonvals + 90)
    thvals = np.deg2rad(90 - latvals)
    rhovals = geometry_params['radius'] * np.sin(thvals)
    xvals = rhovals * np.cos(phvals) + geometry_params['center'][0]
    yvals = rhovals * np.sin(phvals) + geometry_params['center'][1]
    zvals = (geometry_params['radius'] * np.cos(thvals)
             + geometry_params['center'][2])

    geometry_points = {
        'npoints': nlon * nlat,
        'latitude': latvals.flatten(),
        'longitude': lonvals.flatten(),
        'X': xvals.flatten(),
        'Y': yvals.flatten(),
        'Z': zvals.flatten()
    }
    return geometry_points


def _line_geometry(geometry_params: dict) -> dict:
    """Returns a dict containing points for the described line geometry.
    """
    geometry_points = {
        'npoints': geometry_params['npoints'],
        'X': np.linspace(
            geometry_params['r1'][0],
            geometry_params['r2'][0],
            geometry_params['npoints']),
        'Y': np.linspace(
            geometry_params['r1'][1],
            geometry_params['r2'][1],
            geometry_params['npoints']),
        'Z': np.linspace(
            geometry_params['r1'][2],
            geometry_params['r2'][2],
            geometry_params['npoints'])
    }
    return geometry_points


def _rectprism_geometry(geometry_params: dict) -> dict:
    """Returns a dict containing points for the described rectprism geometry.
    """
    npoints = (geometry_params['npoints'][0]
               * geometry_params['npoints'][1]
               * geometry_params['npoints'][2])
    vals = []
    for dim in range(3):
        minval = (geometry_params['center'][dim]
                  - geometry_params['halfwidths'][dim])
        maxval = (geometry_params['center'][dim]
                  + geometry_params['halfwidths'][dim])
        vals.append(np.linspace(
            minval,
            maxval,
            geometry_params['npoints'][dim]
        ))
    xvals, yvals, zvals = np.meshgrid(vals[0], vals[1], vals[2])
    geometry_points = {
        'npoints': npoints,
        'X': xvals.flatten(),
        'Y': yvals.flatten(),
        'Z': zvals.flatten(),
    }
    return geometry_points


def _trajectory_geometry(geometry_params: dict) -> dict:
    """Returns a dict containing points for the described trajectory geometry.

    Assumes format of trajectory file after SWMF SATELLITE command.
    """
    do_read = False
    trajectory_data = []
    with open(geometry_params['trajectory_data'], 'r') as trajectory_file:
        for line in trajectory_file:
            if do_read:
                if len(line.split()) == 10:
                    trajectory_data.append(line.split())
                else:
                    do_read = False
            elif '#START' in line:
                do_read = True
    try:
        assert len(trajectory_data) >= 1
    except:
        raise ValueError(
            'No points could be read from the trajectory file. Consult the '
            'SWMF documentation for advice on trajectory format.'
        )
    geometry_points = {
        'npoints': len(trajectory_data),
        'X': [float(trajectory_point[7])
              for trajectory_point in trajectory_data],
        'Y': [float(trajectory_point[8])
              for trajectory_point in trajectory_data],
        'Z': [float(trajectory_point[9])
              for trajectory_point in trajectory_data],
        'time': [((np.datetime64(
            f'{trajectory_point[0]}'
            f'-{trajectory_point[1]}'
            f'-{trajectory_point[2]}'
            f'T{trajectory_point[3]}'
            f':{trajectory_point[4]}'
            f':{trajectory_point[5]}'
            f'.{trajectory_point[6]}')
                   - np.datetime64('1970-01-01T00:00:00Z'))
                  / np.timedelta64(1, 's'))
                 for trajectory_point in trajectory_data]
    }
    return geometry_points


def _save_hdf5(filename, geometry_params, new_zone, variables) -> None:
    """Save the aux data and a subset of the variables in hdf5 format.
    """
    column_names = [var.name for var in variables]
    tp_data = []
    for var in variables:
        tp_data.append(new_zone.values(var)[:])
    tp_data_np = np.array(tp_data).transpose()
    with h5py.File(filename, 'w-') as h5_file:
        h5_file['data'] = tp_data_np
        h5_file['data'].attrs.update(geometry_params)
        h5_file['data'].attrs['names'] = column_names


def _save_csv(filename, geometry_params, new_zone, variables) -> None:
    """Save the aux data and a subset of the variables in plain-text format.
    """
    aux_data = geometry_params.__repr__() + '\n'
    column_names = variables[0].name.__repr__()
    for var in variables[1:]:
        column_names += ' ' + var.name.__repr__()
    tp_data = []
    for var in variables:
        tp_data.append(new_zone.values(var)[:])
    tp_data_np = np.array(tp_data).transpose()
    np.savetxt(
        filename,
        tp_data_np,
        delimiter=' ',
        header=aux_data + column_names,
        comments=''
    )


def tecplot_interpolate(
        tecplot_plt_file_path: str
        , geometry: str
        , write_as: str
        , filename: str = None
        , tecplot_equation_file_path: str = None
        , tecplot_variable_pattern: str = None
        , verbose: bool = False
        , **kwargs
) -> None:
    """Interpolates Tecplot binary data onto various geometries.

    Args:
        tecplot_plt_file_path (str): Path to the tecplot binary file.
        geometry (str): Type of geometry for interpolation. Supported geometries
            are 'shell', 'line', 'rectprism', or 'trajectory'.
        write_as (str): Type of file to write to. Supported options are 'hdf5',
            'csv', 'tecplot_ascii', and 'tecplot_plt'.
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
            interpolate onto, excluding the north and south polar points.
            Defaults to (360,179).
        r1 (array-like): Argument for the 'line' geometry. Contains the X, Y,
            and Z positions of the point where the line starts. Required.
        r2 (array-like): Argument for the 'line' geometry. Contains the X, Y,
            and Z positions of the point where the line ends. Required.
        npoints (int): Argument for the 'line' geometry. The number of points
            along the line to interpolate onto. Required.
        center (array-like): Argument for the 'rectprism' geometry. Contains the
            X, Y, and Z positions of the center of the rectangular prism.
            Defaults to (0,0,0).
        halfwidths (array-like): Argument for the 'rectprism' geometry. Contains
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
        geometry_params['center'] = geometry_params.get(
            'center'
            , (0.0, 0.0, 0.0)
        )
        geometry_params['npoints'] = geometry_params.get(
            'npoints'
            , (359, 181)
        )
    elif 'rectprism' in geometry_params['kind']:
        geometry_params['center'] = geometry_params.get(
            'center'
            , (0.0, 0.0, 0.0)
        )

    ## check that we support the geometry
    geometry_param_names = {
        'shell': ('radius',),
        'line': ('r1', 'r2', 'npoints'),
        'rectprism': ('halfwidths', 'npoints'),
        'trajectory': ('trajectory_data', 'trajectory_format')
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
        , 'csv'
        , 'tecplot_ascii'
        , 'tecplot_plt'
    )
    if write_as not in file_types:
        raise ValueError(f'File type {write_as} not supported!')

    ## describe the interpolation we're about to do on the data
    if verbose:
        print('Geometry to be interpolated:')
        for key, value in geometry_params.items():
            print(f'\t{key}: {value.__repr__()}')

    ## check whether we are using equations
    ## check that the equations file is there
    use_equations = not tecplot_equation_file_path is None
    if use_equations:
        equations_file = open(tecplot_equation_file_path, 'r')
        equations_file.close()
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
    apply_equations(tecplot_equation_file_path)
    if verbose:
        print('Variables after equations:')
        print(batsrus.variable_names)

    ## create geometry zone
    if 'shell' in geometry_params['kind']:
        geometry_points = _shell_geometry(geometry_params)
    elif 'line' in geometry_params['kind']:
        geometry_points = _line_geometry(geometry_params)
    elif 'rectprism' in geometry_params['kind']:
        geometry_points = _rectprism_geometry(geometry_params)
    elif 'trajectory' in geometry_params['kind']:
        if 'batsrus' in geometry_params['trajectory_format']:
            geometry_points = _trajectory_geometry(geometry_params)

    source_zone = list(batsrus.zones())
    if ('trajectory' in geometry_params['kind']
            and 'tecplot' in geometry_params['trajectory_format']):
        batsrus = tecplot.data.load_tecplot(
            filenames=geometry_params['trajectory_data']
            , read_data_option=tecplot.constant.ReadDataOption.Append
        )
        new_zone = batsrus.zone(-1)
        new_zone.name = 'geometry'
    else:
        new_zone = batsrus.add_ordered_zone(
            'geometry'
            , geometry_points['npoints']
        )
        for i, direction in zip((0, 1, 2), ('X', 'Y', 'Z')):
            new_zone.values(i)[:] = geometry_points[direction][:]

    ## interpolate variables on to the geometry
    if verbose:
        print('Interpolating variables:')
    positions = list(batsrus.variables('*[[]R[]]'))
    variables = list(batsrus.variables(re.compile(tecplot_variable_pattern)))
    if verbose:
        for var in variables:
            print(var.name)
    tecplot.data.operate.interpolate_linear(
        destination_zone=new_zone
        , source_zones=source_zone
        , variables=variables
    )
    ## add variables for shell and trajectory cases
    if 'shell' in  geometry_params['kind']:
        batsrus.add_variable('latitude [deg]')
        new_zone.values('latitude [[]deg[]]')[:] = geometry_points['latitude']
        batsrus.add_variable('longitude [deg]')
        new_zone.values('longitude [[]deg[]]')[:] = geometry_points['longitude']
        variables = variables + list(batsrus.variables('*itude [[]deg[]]'))
    if 'trajectory' in geometry_params['kind']:
        batsrus.add_variable('time')
        if 'batsrus' in geometry_params['trajectory_format']:
            new_zone.values('time')[:] = geometry_points['time']
        variables = variables + [batsrus.variable('time')]

    ## add auxiliary data
    new_zone.aux_data.update(geometry_params)
    if ('trajectory' in geometry_params['kind']
            and 'pandas' in geometry_params['trajectory_format']):
        new_zone.aux_data.update(
            {'trajectory_data': type(geometry_params['trajectory_data'])}
        )

    ## construct default filename
    no_file_name = False
    if filename is None:
        no_file_name = True
        filename = tecplot_plt_file_path[:-4] + f'_{geometry_params["kind"]}'

    ## save zone
    if 'hdf5' in write_as:
        if no_file_name:
            filename += '.h5'
        _save_hdf5(
            filename,
            geometry_params,
            new_zone,
            positions + variables
        )
    elif 'csv' in write_as:
        if no_file_name:
            filename += '.csv'
        _save_csv(
            filename,
            geometry_params,
            new_zone,
            positions + variables
        )
    elif 'tecplot_ascii' in write_as:
        if no_file_name:
            filename += '.dat'
        tecplot.data.save_tecplot_ascii(
            filename
            , zones=new_zone
            , variables=positions + variables
            , use_point_format=True
        )
    elif 'tecplot_plt' in write_as:
        if no_file_name:
            filename += '.plt'
        tecplot.data.save_tecplot_plt(
            filename
            , zones=new_zone
            , variables=positions + variables
        )
    if verbose:
        print(f'Wrote {filename}')
