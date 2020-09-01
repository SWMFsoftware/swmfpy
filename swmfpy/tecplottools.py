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
    'bracketify',
    'write_zone',
    'interpolate_zone_to_geometry'
]
__author__ = 'Camilla D. K. Harris'
__email__ = 'cdha@umich.edu'

import h5py
import numpy as np
import tecplot


def _get_variable_names(variables) -> list:
    """For getting the names of a group of Tecplot variables."""
    return [var.name for var in variables]


def _shell_geometry(geometry_params: dict) -> dict:
    """Returns a dict containing points for the described shell geometry."""
    nlon = geometry_params['npoints'][0] # 360
    nlat = geometry_params['npoints'][1] # 179
    lons = np.linspace(0, 360, nlon, endpoint=False)
    dlat = 180/(nlat + 1)
    lats = np.linspace(-90.0+dlat, 90.0-dlat, nlat)

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
    """Returns a dict containing points for the described line geometry."""
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
    """Returns a dict containing points for the described rectprism geometry."""
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

    Assumes format of trajectory file after SWMF `SATELLITE` command.
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


def _save_hdf5(
        filename: str,
        geometry_params: dict,
        new_zone,
        variables
) -> None:
    """Save the aux data and a subset of the variables in hdf5 format."""
    column_names = _get_variable_names(variables)
    tp_data = []
    for var in variables:
        tp_data.append(new_zone.values(var)[:])
    tp_data_np = np.array(tp_data).transpose()
    with h5py.File(filename, 'w-') as h5_file:
        h5_file['data'] = tp_data_np
        h5_file['data'].attrs.update(geometry_params)
        h5_file['data'].attrs['names'] = column_names


def _save_csv(
        filename: str,
        geometry_params: dict,
        new_zone,
        variables
) -> None:
    """Save the aux data and a subset of the variables in plain-text format."""
    aux_data = geometry_params.__repr__() + '\n'
    column_names = variables[0].name.__repr__()
    for var in variables[1:]:
        column_names += ',' + var.name.__repr__()
    tp_data = []
    for var in variables:
        tp_data.append(new_zone.values(var)[:])
    tp_data_np = np.array(tp_data).transpose()
    np.savetxt(
        filename,
        tp_data_np,
        delimiter=',',
        header=aux_data + column_names,
        comments=''
    )


def _add_variable_value(dataset, variable_name: str, zone, values) -> None:
    """Adds and populates a new variable to a zone in a dataset."""
    dataset.add_variable(variable_name)
    zone.values(bracketify(variable_name))[:] = values


def apply_equations(eqn_path: str, verbose: bool = False) -> None:
    """Apply a Tecplot-formatted equations file to the active dataset.

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


def bracketify(variable_name: str) -> str:
    """Surrounds square brackets with more brackets in a string.

    This is helpful for accessing Tecplot variables.

    Args:
        variable_name (str): A string which may contain the meta-characters * ?
          [ or ].

    Examples:
        In a dataset which contains the variable 'X [R]',
        ```python
        print(dataset.variable_names)
        # ['X [R]', ... ]
        ```
        The following will fail:
        ```python
        print(dataset.variable('X [R]').name)
        # TecplotPatternMatchWarning: no variables found matching: "X [R]" For
        # a literal match, the meta-characters: * ? [ ] must be wrapped in 
        # square-brackets. For example, "[?]" matches the character "?"...
        ```
        However,
        ```python
        print(dataset.variable(tpt.bracketify('X [R]')).name)
        ```
        will succeed.
    """
    translation = {
        '[':'[[]',
        ']':'[]]',
        '*':'[*]',
        '?':'[?]'
    }
    return variable_name.translate(str.maketrans(translation))


def write_zone(
        tecplot_dataset
        , tecplot_zone
        , write_as: str
        , filename: str
        , variables=None
        , verbose: bool = False
) -> None:
    """Writes a tecplot zone to various formats.

    Args:
        tecplot_dataset (tecplot.data.Dataset): The dataset to save.
        tecplot_zone (tecplot.data.zone): The zone to save.
        write_as (str): Type of file to write to. Supported options are `hdf5`,
          `csv`, `tecplot_ascii`, and `tecplot_plt`.
        filename (str): Name of the file to write to.
        variables (list): (Optional) Specify a subset of the dataset variables
          to save. This option may decrease the size of the output. Default
          behavior is to save all variables.
        verbose: (Optional) Print diagnostic information. Defaults to False.

    Examples:
        ```python
        import tecplot
        import swmfpy.tecplottools as tpt

        ## load a dataset and configure the layout
        dataset = tecplot.data.load_tecplot(
            '3d__mhd_1_n00000100.plt')
        frame = tecplot.active_frame()
        frame.plot_type = tecplot.constant.PlotType.Cartesian3D
        plot = frame.plot()

        ## set the vector variables
        plot.vector.u_variable = dataset.variable(4)
        plot.vector.v_variable = dataset.variable(5)
        plot.vector.w_variable = dataset.variable(6)

        ## seed and extract a streamtrace
        plot.streamtraces.add(
            seed_point=(1.5, 1.0, 0.0),
            stream_type=tecplot.constant.Streamtrace.VolumeLine
        )
        streamtrace_zones = plot.streamtraces.extract()
        new_zone = next(streamtrace_zones)

        ## write the new zone to hdf5 format
        tpt.write_zone(
            tecplot_dataset=dataset,
            tecplot_zone=new_zone,
            write_as='hdf5',
            filename='streamtrace.h5'
        )
        ```
    """
    if verbose and variables:
        print('Saving variables:')
        print(_get_variable_names(variables).__repr__())
    aux_data = tecplot_zone.aux_data.as_dict()
    if verbose:
        print('Attaching auxiliary data:')
        print(aux_data.__repr__())
    ## save zone
    if 'hdf5' in write_as:
        if not variables:
            variables = list(tecplot_dataset.variables())
        _save_hdf5(
            filename,
            aux_data,
            tecplot_zone,
            variables
        )
    elif 'csv' in write_as:
        if not variables:
            variables = list(tecplot_dataset.variables())
        _save_csv(
            filename,
            aux_data,
            tecplot_zone,
            variables
        )
    elif 'tecplot_ascii' in write_as:
        tecplot.data.save_tecplot_ascii(
            filename
            , zones=tecplot_zone
            , variables=variables
            , use_point_format=True
        )
    elif 'tecplot_plt' in write_as:
        tecplot.data.save_tecplot_plt(
            filename
            , zones=tecplot_zone
            , variables=variables
        )
    else:
        raise ValueError(f'File type {write_as} not supported!')
    if verbose:
        print(f'Wrote {filename}')


def _assign_geometry_defaults(
        geometry: str,
        default_params: dict,
        geometry_params: dict
) -> dict:
    """Checks parameters with defaults and assigns them.

    If the parameters are already set nothing will change.

    Args:
        geometry (str): String identifying the geometry to look for.
        default_params (dict): Dictionary of the default parameters.
        geomatry_params (dict): Dictionary in which to look for and set
          parameters.
    """
    if geometry in geometry_params['geometry']:
        for key, value in default_params.items():
            geometry_params[key] = geometry_params.get(
                key,
                value
            )
    return geometry_params


def _check_geometry_requirements(
        geometry_requirements: dict,
        geometry_params: dict
) -> None:
    """Checks that the required kwargs for the given geometry have been set.
    """
    if geometry_params['geometry'] not in geometry_requirements:
        raise ValueError(f'Geometry {geometry_params["geometry"]} '
                         'not supported!')
    for param in geometry_requirements[geometry_params['geometry']]:
        if param not in geometry_params:
            raise TypeError(
                f'Geometry {geometry_params["geometry"]} '
                f'requires argument {param}!')


def _get_geometry_points(
        geometry_params: dict
) -> dict:
    """Select the right function to calculate the geometry points."""
    if 'shell' in geometry_params['geometry']:
        geometry_points = _shell_geometry(geometry_params)
    elif 'line' in geometry_params['geometry']:
        geometry_points = _line_geometry(geometry_params)
    elif 'rectprism' in geometry_params['geometry']:
        geometry_points = _rectprism_geometry(geometry_params)
    elif ('trajectory' in geometry_params['geometry']
          and 'batsrus' in geometry_params['trajectory_format']):
        geometry_points = _trajectory_geometry(geometry_params)
    else:
        geometry_points = None
    return geometry_points


def interpolate_zone_to_geometry(
        dataset
        , source_zone
        , geometry: str
        , variables: list = None
        , verbose: bool = False
        , **kwargs
):
    """Interpolates Tecplot binary data onto various geometries.

    Returns a tecplot zone object.

    Args:
        dataset (tecplot.data.Dataset): The loaded Tecplot dataset.
        source_zone (tecplot.data.zone): The Tecplot zone to interpolate onto
          the geometry.
        geometry (str): Type of geometry for interpolation. Supported geometries
          are `shell`, `line`, `rectprism`, or `trajectory`. See below for the
          required keyword arguments for each geometry.
        variables (list): (Optional) Subset of variables to interpolate. Default
          behavior is to interpolate all variables.
        verbose (bool): (Optional) Print diagnostic information. Defaults to
          False.
        **center (array-like): Argument for the `shell` geometry. Contains the
          X, Y, and Z positions of the shell. Defaults to (0,0,0).
        **radius (float): Required argument for the `shell` geometry.
        **npoints (array-like): Argument for the `shell` geometry. Contains the
          number of points in the azimuthal and polar directions to interpolate
          onto, excluding the north and south polar points. Defaults to
          (360, 179).
        **r1 (array-like): Required argument for the `line` geometry. Contains
          the X, Y, and Z positions of the point where the line starts.
        **r2 (array-like): Required argument for the `line` geometry. Contains
          the X, Y, and Z positions of the point where the line ends.
        **npoints (int): Required argument for the `line` geometry. The number
          of points along the line to interpolate onto.
        **center (array-like): Argument for the `rectprism` geometry. Contains
          the X, Y, and Z positions of the center of the rectangular prism.
          Defaults to (0,0,0).
        **halfwidths (array-like): Required argument for the `rectprism`
          geometry. Contains the half widths of the rectangular prism in the X,
          Y, and Z directions.
        **npoints (array-like): Required argument for the `rectprism` geometry.
          Contains the number of points in the X, Y, and Z directions to
          interpolate onto.
        **trajectory_data (str): Required argument for the `trajectory`
          geometry. The path to the ASCII trajectory data file.
        **trajectory_format (str): Required argument for the `trajectory`
          geometry. The format of the trajectory data file. Supported formats
          are `tecplot` (data is a tecplot zone with 3D positional variables)
          and `batsrus` (data is formatted as described for the `SATELLITE`
          command, see SWMF documentation).

    Examples:
        ```python
        import tecplot
        import swmfpy.tecplottools as tpt

        tecplot.session.connect(port=7600)

        ## Load a dataset and configure the layout.
        dataset = tecplot.data.load_tecplot('3d__mhd_1_n00000100.plt')

        ## Create a new zone with the specified geometry
        ## and interpolate data onto it.

        ## geometry: shell
        tpt.interpolate_zone_to_geometry(
            dataset=dataset,
            source_zone=dataset.zone(0),
            geometry='shell',
            radius=1.5,
            npoints=(4,3)
        )

        ## geometry: line
        tpt.interpolate_zone_to_geometry(
            dataset=dataset,
            source_zone=dataset.zone(0),
            geometry='line',
            r1=[1.0, 0.0, 0.0],
            r2=[3.0, 0.0, 0.0],
            npoints=100
        )

        ## geometry: rectangular prism
        new_zone = tpt.interpolate_zone_to_geometry(
            dataset=dataset,
            source_zone=dataset.zone(0),
            geometry='rectprism',
            center=[0.0, 0.0, 0.0],
            halfwidths=[2.0, 2.0, 2.0],
            npoints=[5, 5, 5]
        )

        ## geometry: spacecraft trajectory as specified for the
        ## BATSRUS SATELLITE command
        tpt.interpolate_zone_to_geometry(
            dataset=dataset,
            source_zone=dataset.zone(0),
            geometry='trajectory',
            trajectory_format='batsrus',
            trajectory_data='satellite_e4.dat'
        )

        ## The new zones are labeled with the name of the geometry and can be
        ## manipulated in the Tecplot GUI.
        ```

    """
    if verbose:
        print('Collecting parameters')

    ## collect the geometry parameters
    geometry_params = {
        'geometry':geometry
    }
    geometry_params.update(kwargs)

    if verbose:
        print('Adding defaults')
    geometry_params = _assign_geometry_defaults(
        'shell',
        {
            'center':(0.0, 0.0, 0.0),
            'npoints':(359, 181)
        },
        geometry_params
    )
    geometry_params = _assign_geometry_defaults(
        'rectprism',
        {
            'center':(0.0, 0.0, 0.0),
        },
        geometry_params
    )

    _check_geometry_requirements(
        {
            'shell': ('radius',),
            'line': ('r1', 'r2', 'npoints'),
            'rectprism': ('halfwidths', 'npoints'),
            'trajectory': ('trajectory_data', 'trajectory_format')
        },
        geometry_params
    )

    if verbose:
        ## describe the interpolation we're about to do on the data
        print('Geometry to be interpolated:')
        for key, value in geometry_params.items():
            print(f'\t{key}: {value.__repr__()}')

        ## describe the loaded tecplot data
        print('Loaded tecplot data with variables:')
        print(dataset.variable_names)

    ## create geometry zone
    geometry_points = _get_geometry_points(
        geometry_params
    )
    if ('trajectory' in geometry_params['geometry']
            and 'tecplot' in geometry_params['trajectory_format']):
        dataset = tecplot.data.load_tecplot(
            filenames=geometry_params['trajectory_data']
            , read_data_option=tecplot.constant.ReadDataOption.Append
        )
        dataset.zone(-1).name = geometry_params['geometry']
    else:
        dataset.add_ordered_zone(
            geometry_params['geometry']
            , geometry_points['npoints']
        )
        for i, direction in zip((0, 1, 2), ('X', 'Y', 'Z')):
            dataset.zone(geometry_params['geometry']).values(i)[:] = \
                 geometry_points[direction][:]

    ## interpolate variables on to the geometry
    if verbose and variables:
        print('Interpolating variables:')
        print(_get_variable_names(variables).__repr__())

    ## dataset.variables('...') will return a generator of variables.
    ## This call will break if `variables` is not recast as a list before
    ## passing it to the function. Why?????
    tecplot.data.operate.interpolate_linear(
        destination_zone=dataset.zone(geometry_params['geometry']),
        source_zones=source_zone,
        variables=variables
    )

    ## add variables for shell and trajectory cases
    if 'shell' in  geometry_params['geometry']:
        _add_variable_value(
            dataset,
            'latitude [deg]',
            dataset.zone(geometry_params['geometry']),
            geometry_points['latitude']
        )
        _add_variable_value(
            dataset,
            'longitude [deg]',
            dataset.zone(geometry_params['geometry']),
            geometry_points['longitude']
        )
    if ('trajectory' in geometry_params['geometry']
            and 'batsrus' in geometry_params['trajectory_format']):
        _add_variable_value(
            dataset,
            'time',
            dataset.zone(geometry_params['geometry']),
            geometry_points['time']
        )
        geometry_params['time_seconds_since'] = '1970-01-01T00:00:00Z'

    ## add auxiliary data
    dataset.zone(geometry_params['geometry']).aux_data.update(geometry_params)

    return dataset.zone(geometry_params['geometry'])
