# Table of Contents

* [swmfpy](#swmfpy)
  * [write\_imf\_from\_omni](#swmfpy.write_imf_from_omni)
* [swmfpy.web](#swmfpy.web)
  * [get\_omni\_data](#swmfpy.web.get_omni_data)
  * [download\_magnetogram\_hmi](#swmfpy.web.download_magnetogram_hmi)
  * [download\_magnetogram\_adapt](#swmfpy.web.download_magnetogram_adapt)
* [swmfpy.io](#swmfpy.io)
  * [write\_imf\_input](#swmfpy.io.write_imf_input)
  * [read\_wdc\_ae](#swmfpy.io.read_wdc_ae)
  * [read\_wdc\_asy\_sym](#swmfpy.io.read_wdc_asy_sym)
  * [read\_gm\_log](#swmfpy.io.read_gm_log)
* [swmfpy.paramin](#swmfpy.paramin)
  * [replace\_command](#swmfpy.paramin.replace_command)
  * [read\_command](#swmfpy.paramin.read_command)
* [swmfpy.tools](#swmfpy.tools)
  * [interp\_nans](#swmfpy.tools.interp_nans)
  * [carrington\_rotation\_number](#swmfpy.tools.carrington_rotation_number)
* [swmfpy.tecplottools](#swmfpy.tecplottools)
  * [apply\_equations](#swmfpy.tecplottools.apply_equations)
  * [bracketify](#swmfpy.tecplottools.bracketify)
  * [write\_zone](#swmfpy.tecplottools.write_zone)
  * [interpolate\_zone\_to\_geometry](#swmfpy.tecplottools.interpolate_zone_to_geometry)

<a name="swmfpy"></a>
# swmfpy

A collection of tools to read, write, visualize with the
Space Weather Modeling Framework (SWMF).

### Modules

These are automatically imported.

- `swmfpy.io` Input/Output tools.
- `swmfpy.paramin` PARAM.in editing tools.
- `swmfpy.web` Internet data downloading/uploading tools.

### Extra Modules

These must be imported manually.

- `swmfpy.tools` Tools used in swmfpy. You might find these useful but it is
  unecessary.
- `swmfpy.tecplottools` Tools for working with the Tecplot visualization
  software. Requires a Tecplot license and the pytecplot python package.

<a name="swmfpy.write_imf_from_omni"></a>
#### write\_imf\_from\_omni

```python
write_imf_from_omni(time_from, time_to, filename='IMF.dat', **kwargs)
```

Writes an IMF.dat file for the geospace model runs for a specific time
period.

**Arguments**:

- `time_from` _datetime.datetime_ - Time to begin omni data retrieval
- `time_to` _datetime.datetime_ - Time to end omni data retrieval
- `filename` _str_ - The filename for the dat file, defaults to 'IMF.dat'.
  
  **kwargs:
  see `swmfpy.io.write_imf_input()` and `swmfpy.web.get_omni_data()`
  

**Returns**:

- `(dict)` - Dictionary of omni data.
  

**Examples**:

  Using this function is simple:
  ```python
  import swmfpy
  import datetime as dt
  times = (dt.datetime(2014, 2, 2), dt.datetime(2014, 2, 4))
  # Usually the kwargs are unecessary
  swmfpy.write_imf_input(*times)
  # Sometimes this
  swmfpy.write_imf_input(*times, filename='run/IMF.dat')
  ```

<a name="swmfpy.web"></a>
# swmfpy.web

### Tools to download/upload data on the web

Here are a collection of tools to work with data on the internet. Thus,
this module mostly requires an internet connection. Which on some
supercomputers would be turned off during a job run. In scripts, make sure to
use these to preprocess before submitting jobs.

<a name="swmfpy.web.get_omni_data"></a>
#### get\_omni\_data

```python
@lru_cache(maxsize=4)
get_omni_data(time_from, time_to, **kwargs)
```

Retrieve omni solar wind data over http.

This will download omni data from https://spdf.gsfc.nasa.gov/pub/data/omni
and put it into a dictionary. If your data is large, then make a csv and
use swmfpy.io.read_omni_data().

Note that calling this more than once with the same arguments will point to
your original dictionary that it created. This is to speed up code that
calls this multiple times as it requires internet access and download.
If you mutate your original try doing an omni_dict2 = omni_dict1.copy()
and mutate the other one.

**Arguments**:

- `time_from` _datetime.datetime_ - The start time of the solar wind
  data that you want to receive.
- `time_to` _datetime.datetime_ - The end time of the solar wind data
  you want to receive.
  **kwargs:
- `original_colnames` _bool_ - Use the original column names from the
  spdf specification. The alternative is
  nicer and shorter names. Defaults to
  False.
- `resolution` _str_ - (default: 'high') Here you can choose 'high' or
  'low' resolution omni data. Some columns appear
  in one but not the other.
  

**Returns**:

- `dict` - This will be a list of *all* columns
  available in the omni data set.
  

**Examples**:

  ```python
  import datetime
  import swmfpy.web
  
  storm_start = datetime.datetime(year=2000, month=1, day=1)
  storm_end = datetime.datetime(year=2000, month=2, day=15)
  data = swmfpy.web.get_omni_data(time_from=storm_start,
  time_to=storm_end)
  # or for low res
  data = swmfpy.web.get_omni_data(time_from=storm_start,
  time_to=storm_end,
  resolution='low')
  ```

<a name="swmfpy.web.download_magnetogram_hmi"></a>
#### download\_magnetogram\_hmi

```python
download_magnetogram_hmi(mag_time, hmi_map='hmi.B_720s', **kwargs)
```

Downloads HMI vector magnetogram fits files.

This will download vector magnetogram FITS files from
Joint Science Operations Center (JSOC) near a certain hour.

**Arguments**:

- `mag_time` _datetime.datetime_ - Time after which to find
  vector magnetograms.
- `hmi_map` _str_ - JSOC prefix for hmi maps. Currently can only do
  'hmi.B_720s' and 'hmi.b_synoptic.small'.
  
  **kwargs:
- `download_dir` _str_ - Relative directory to download to.
- `verbose` _bool_ - (default False) print out the files it's downloading.
  

**Returns**:

- `str` - list of filenames downloaded.
  

**Raises**:

- `ImportError` - If module `drms` is not found.
- `FileNotFoundError` - If the JSOC doesn't have the magnetograms for that
  time.
  

**Examples**:

  ```python
  from swmfpy.web import download_magnetogram_hmi
  import datetime as dt
  
  # I am interested in the hmi vector magnetogram from 2014, 2, 18
  time_mag = dt.datetime(2014, 2, 18, 10)  # Around hour 10
  
  # Calling it will download
  filenames = download_magnetogram_hmi(mag_time=time_mag,
  hmi_map='B_720s',
  download_dir='mydir/')
  
  # To see my list
  print('The magnetograms I downloaded are:', filenames)
  
  # You may call and ignore the file list
  download_magnetogram_hmi(mag_time=time_mag,
  hmi_map='b_synoptic_small',
  download_dir='mydir')
  ```

<a name="swmfpy.web.download_magnetogram_adapt"></a>
#### download\_magnetogram\_adapt

```python
download_magnetogram_adapt(time, map_type='fixed', **kwargs)
```

This routine downloads GONG ADAPT magnetograms.

Downloads ADAPT magnetograms from ftp://gong2.nso.edu/adapt/maps/gong/
to a local directory. It will download all maps with the regex file
pattern: adapt4[0,1]3*yyyymmddhh

**Arguments**:

- `time` _datetime.datetime_ - Time in which you want the magnetogram.
- `map_type` _str_ - (default: 'fixed')
  Choose either 'fixed' or 'central' for
  the map type you want.
  
  **kwargs:
- `download_dir` _str_ - (default is current dir) Relative directory
  where you want the maps to be downloaded.
  

**Returns**:

- `str` - First unzipped filename found.
  

**Raises**:

- `NotADirectoryError` - If the adapt maps directory
  is not found on the server.
- `ValueError` - If map_type is not recognized.
  (i.e. not 'fixed' or 'central')
- `FileNotFoundError` - If maps were not found.
  

**Examples**:

  ```python
  import datetime as dt
  
  # Use datetime objects for the time
  time_flare = dt.datetime(2018, 2, 12, hour=10)
  swmfpy.web.download_magnetogram_adapt(time=time_flare,
  map_type='central',
  download_dir='./mymaps/')
  ```

<a name="swmfpy.io"></a>
# swmfpy.io

### Input/Output tools

Here are tools to read and write files relating to SWMF.

<a name="swmfpy.io.write_imf_input"></a>
#### write\_imf\_input

```python
write_imf_input(imf_data, filename='IMF.dat', **kwargs)
```

Creates the IMF.dat input file for the SWMF BATS-R-US geospace model.

`imf_data` must be a dictionary of array_like objects with same length
in data. In swmfpy Pythonic versions are always preferred so the 'times'
must be `datetime.datetime` array.
imf_data = dict(times, bx, by, bz, vx, vy, vz, density, temperature)

**Arguments**:

- `imf_data` _dict_ - This dictionary contains the solar wind data.
- `filename` _str_ - (default: 'IMF.dat') Filename to write to.
  **kwargs:
- `commands` _[str]_ - (default: None) List of commands to write to imf
  input file (indexed by line then by tabs on same
  line). *Note*: Must be a list if have one command
  str.
  

**Raises**:

- `TypeError` - If commands is not a list or tuple. It must be at least a
  one element list of strings.
- `AssertionError` - If inputs aren't prepared properly (key names)
  

**Examples**:

  ```python
  from swmfpy.io import write_imf_input
  
  # Prepare imf dictionary: imf_data
  write_imf_input(imf_data, filename='run/IMF.dat')
  ```

<a name="swmfpy.io.read_wdc_ae"></a>
#### read\_wdc\_ae

```python
read_wdc_ae(wdc_filename)
```

Read an auroral electrojet (AE) indeces from Kyoto's World Data Center
text file into a dictionary of lists.

**Arguments**:

  
- `wdc_filename` _str_ - Filename of wdc data from
  http://wdc.kugi.kyoto-u.ac.jp/

**Returns**:

- `dict` - Auroral indeces 'AL', 'AE', 'AO', 'AU'
- `datetime.datetime` - 'times'
- `int` - 'values'

<a name="swmfpy.io.read_wdc_asy_sym"></a>
#### read\_wdc\_asy\_sym

```python
read_wdc_asy_sym(wdc_filename)
```

Reads a WDC file for ASY/SYM data.

Reads an ASY/SYM file downloaded from
http://wdc.kugi.kyoto-u.ac.jp/aeasy/index.html
and puts it into a dictionary.

**Arguments**:

- `wdc_filename` _str_ - Relative filename (or file handle no.) to read.
  

**Returns**:

- `dict` - of values. {'[ASY-SYM]-[D-H]': 'times': [], 'values': []}
  

**Examples**:

  ```python
  indeces = swmfpy.io.read_wdc_asy_sym('wdc.dat')
  # Plot data
  plt.plot(indeces['SYM-H']['times'],
  indeces['SYM-H']['values'],
  label='SYM-H [nT]'
  )
  plt.xlabel('Time [UT]')
  ```
  
  Important to note if there is bad data it will be filled as None.

<a name="swmfpy.io.read_gm_log"></a>
#### read\_gm\_log

```python
read_gm_log(filename, colnames=None, dtypes=None, index_time=True)
```

Make a dictionary out of the indeces outputted
from the GM model log.

**Arguments**:

- `filename` _str_ - The relative filename as a string. (or file handle no.)
- `colnames` _[str]_ - (default: None) Supply the name of the columns.
  If None it will use second line
  of log file.
- `dtypes` _[types]_ - (default: None) Provide types for the columns, if
  None then all will be float.
- `index_time` _bool_ - (default: True) Make a column of dt.datetime objects
  in dictionary key 'Time [UT]'.
  

**Returns**:

- `dict` - Dictionary of the log file
  

**Examples**:

  To plot AL and Dst get the log files
  ```python
  geo = swmfpy.io.read_gm_log('run/GM/IO2/geoindex_e20140215-100500.log')
  dst = swmfpy.io.read_gm_log('run/GM/IO2/log_e20140215-100500.log')
  
  # Plot AL indeces
  plt.plot(geo['times', geo['AL'])
  ```

<a name="swmfpy.paramin"></a>
# swmfpy.paramin

### Editing PARAM.in files

These tools are to help script the editing and reading of PARAM.in files.

<a name="swmfpy.paramin.replace_command"></a>
#### replace\_command

```python
replace_command(parameters, input_file, output_file='PARAM.in')
```

Replace values for the parameters in a PARAM.in file.

Note, if you have repeat commands this will replace all the repeats.

**Arguments**:

- `parameters` _dict_ - Dictionary of strs with format
  replace = '#COMMAND': ['value', 'comments', ...]
  This is case sensitive.
- `input_file` _str_ - String of PARAM.in file name.
- `output_file` _str_ - (default 'PARAM.in') The output file to write to.
  A value of None will not output a file.

**Returns**:

  A list of lines of the PARAM.in file that would be outputted.
  

**Raises**:

- `TypeError` - If a value given couldn't be converted to string.
  

**Examples**:

  ```python
  change = {}
  change['#SOLARWINDFILE'] = [['T', 'UseSolarWindFile'],
  ['new_imf.dat', 'NameSolarWindFile']]
  # This will overwrite PARAM.in
  swmfpy.paramin.replace('PARAM.in.template', change)
  ```

<a name="swmfpy.paramin.read_command"></a>
#### read\_command

```python
read_command(command, paramin_file='PARAM.in', **kwargs)
```

Get parameters of a certain command in PARAM.in file.

This will find the #COMMAND and return a list of
values for the parameters.

**Arguments**:

- `command` _str_ - This is the #COMMAND you're looking for.
- `paramin_file` _str_ - (default: 'PARAM.in') The file in which you're
  looking for the command values.
  **kwargs:
- `num_of_values` _int_ - (default: None) Number of values to take from
  command.
  

**Returns**:

- `list` - Values found for the #COMMAND in file. Index 0 is
  #COMMAND and the values follow (1 for first argument...)
  

**Raises**:

- `ValueError` - When the #COMMAND is not found.
  

**Examples**:

  ```python
  start_time = swmfpy.paramin.read_command('#STARTTIME')
  end_time = swmfpy.paramin.read_command('#ENDTIME')
  print('Starting month is ', start_time[1])
  print('Ending month is ', end_time[1])
  ```
  
  This will treat all following lines as values for the command. To suppress
  this, try using the `num_of_values` keyword. This is helpful if your
  PARAM.in is comment heavy.

<a name="swmfpy.tools"></a>
# swmfpy.tools

Tools to be used in swmfpy functions and classes. Some of the functions are
*hidden functions*.

<a name="swmfpy.tools.interp_nans"></a>
#### interp\_nans

```python
interp_nans(x_vals, y_vals)
```

Returns a numpy array with NaNs interpolated.

**Arguments**:

  x_vals (np.array):
  x values to interpolate.
  y_vals (np.array):
  y values including NaNs.
  

**Returns**:

- `(np.array)` - numpy array with NaNs interpolated.

<a name="swmfpy.tools.carrington_rotation_number"></a>
#### carrington\_rotation\_number

```python
carrington_rotation_number(the_time='now')
```

Returns the carrington rotation

**Arguments**:

- `the_time` _datetime.datetime/str_ - The time to convert to carrington
  rotation.
  

**Returns**:

- `(int)` - Carrington Rotation

<a name="swmfpy.tecplottools"></a>
# swmfpy.tecplottools

Tools for working with the Tecplot visualization software.

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

<a name="swmfpy.tecplottools.apply_equations"></a>
#### apply\_equations

```python
apply_equations(eqn_path: str, verbose: bool = False) -> None
```

Apply an equations file in the Tecplot macro format to the active dataset

Please reference the Tecplot User's Manual for more details on
equation files and syntax. It is recommended to use this function with eqn
files generated with the Tecplot GUI.
See [TECPLOT](TECPLOT.markdown) for tips on using pytecplot.

**Arguments**:

  eqn_file_path (str):
  The path to the equation macro file
  (typically with extension `.eqn`).
  verbose (bool):
  (Optional) Whether or not to print the equations as they
  are applied. Default behavior is silent.
  

**Examples**:

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

<a name="swmfpy.tecplottools.bracketify"></a>
#### bracketify

```python
bracketify(variable_name: str) -> str
```

Surrounds square brackets with more brackets in a string.

This is helpful for accessing Tecplot variables.

**Arguments**:

  variable_name (str):
  A string which may contain the meta-characters * ?  [ or ].
  

**Examples**:

  In a dataset which contains the variable 'X [R]',
  ```python
  print(dataset.variable_names)
  # ['X [R]', ... ]
  ```
  The following will fail:
  ```python
  print(dataset.variable('X [R]').name)
  # TecplotPatternMatchWarning: no variables found matching: "X [R]" For
  a literal match, the meta-characters: * ? [ ] must be wrapped in square-
  # For example, "[?]" matches the character "?"...
  ```
  However,
  ```python
  print(dataset.variable(tpt.bracketify('X [R]')).name)
  ```
  will succeed.

<a name="swmfpy.tecplottools.write_zone"></a>
#### write\_zone

```python
write_zone(tecplot_dataset, tecplot_zone, write_as: str, filename: str, variables=None, verbose: bool = False) -> None
```

Writes a tecplot zone to various formats.

**Arguments**:

  tecplot_dataset (tecplot.data.dataset.Dataset):
  The dataset to save.
  tecplot_zone (tecplot.data.dataset.Zone):
  The zone to save.
  write_as (str):
  Type of file to write to. Supported options are 'hdf5',
  'csv', 'tecplot_ascii', and 'tecplot_plt'.
  filename (str):
  Name of the file to write to.
  variables (list(tecplot.data.dataset.Variable)):
  (Optional) Specify a subset of the dataset variables to
  save. This option may decrease the size of the output. Default
  behavior is to save all variables.
  verbose:
  (Optional) Print diagnostic information. Defaults to False.
  

**Examples**:

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

<a name="swmfpy.tecplottools.interpolate_zone_to_geometry"></a>
#### interpolate\_zone\_to\_geometry

```python
interpolate_zone_to_geometry(dataset, source_zone, geometry: str, variables: list = None, verbose: bool = False, **kwargs)
```

Interpolates Tecplot binary data onto various geometries.

**Arguments**:

  dataset:
  The loaded Tecplot dataset.
  source_zone:
  The Tecplot zone to interpolate onto the geometry.
  geometry (str):
  Type of geometry for interpolation. Supported geometries
  are 'shell', 'line', 'rectprism', or 'trajectory'. See below for the
  required keyword arguments for each geometry.
  variables (list):
  (Optional) Subset of variables to interpolate. Default
  behavior is to interpolate all variables.
  verbose:
  (Optional) Print diagnostic information. Defaults to False.
  
  **kwargs:
- `center` _array-like_ - Argument for the 'shell' geometry. Contains the X,
  Y, and Z positions of the shell. Defaults to (0,0,0).
- `radius` _float_ - Argument for the 'shell' geometry. Required.
- `npoints` _array-like_ - Argument for the 'shell' geometry. Contains the
  number of points in the azimuthal and polar directions to
  interpolate onto, excluding the north and south polar points.
  Defaults to (360,179).
- `r1` _array-like_ - Argument for the 'line' geometry. Contains the X, Y,
  and Z positions of the point where the line starts. Required.
- `r2` _array-like_ - Argument for the 'line' geometry. Contains the X, Y,
  and Z positions of the point where the line ends. Required.
- `npoints` _int_ - Argument for the 'line' geometry. The number of points
  along the line to interpolate onto. Required.
- `center` _array-like_ - Argument for the 'rectprism' geometry. Contains the
  X, Y, and Z positions of the center of the rectangular prism.
  Defaults to (0,0,0).
- `halfwidths` _array-like_ - Argument for the 'rectprism' geometry. Contains
  the half widths of the rectangular prism in the X, Y, and Z
  directions. Required.
- `npoints` _array-like_ - Argument for the 'rectprism' geometry. Contains
  the number of points in the X, Y, and Z directions to interpolate
  onto. Required.
- `trajectory_data` _str_ - Argument for the 'trajectory' geometry. The path
  to the ASCII trajectory data file. Required.
- `trajectory_format` _str_ - Argument for the 'trajectory' geometry. The
  format of the trajectory data file. Supported formats are 'tecplot'
  (data is a tecplot zone with 3D positional variables and 'time') and
  'batsrus' (data is formatted as described for the `SATELLITE`
  command, see SWMF documentation). Required.
  

**Examples**:

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
  ## BATSRUS `SATELLITE` command
  tpt.interpolate_zone_to_geometry(
  dataset=dataset,
  source_zone=dataset.zone(0),
  geometry='trajectory',
  trajectory_format='batsrus',
  trajectory_data='./test_data/satellite_e4.dat'
  )
  
  ## The new zones are labeled with the name of the geometry and can be
  ## manipulated in the Tecplot GUI.
  ```

