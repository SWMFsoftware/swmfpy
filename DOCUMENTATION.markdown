<a name=".swmfpy"></a>
## swmfpy

SWMF Tools
==========

A collection of tools to read, write, visualize with the
Space Weather Modeling Framework (SWMF).

Modules
-------

These are automatically imported.

- swmfpy.io: Input/Output tools.
- swmfpy.paramin: PARAM.in editing tools.
- swmfpy.web: Internet data downloading/uploading tools.

Extra Modules
-------------

These are not automatically imported. Might have extra dependancies.

*None yet.*

<a name=".swmfpy.web"></a>
## swmfpy.web

Tools to retrieve and send data on the web.

Here are a collection of tools to work with data on the internet. Thus,
this module mostly requires an internet connection.

<a name=".swmfpy.web.get_omni_data"></a>
#### get\_omni\_data

```python
get_omni_data(time_from, time_to, **kwargs)
```

Retrieve omni solar wind data over http.

This will download omni data from https://spdf.gsfc.nasa.gov/pub/data/omni
and put it into a dictionary. If your data is large, then make a csv and
use swmfpy.io.read_omni_data().

**Arguments**:

- `time_from` _datetime.datetime_ - The start time of the solar wind
  data that you want to receive.
- `time_to` _datetime.datetime_ - The end time of the solar wind data
  you want to receive.
  

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
  ```

<a name=".swmfpy.web.download_magnetogram_adapt"></a>
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

<a name=".swmfpy.io"></a>
## swmfpy.io

Input/Output tools

Here are tools to read and write files relating to SWMF.

TODO: Move pandas dependancy elsewhere.

<a name=".swmfpy.io.read_wdc_ae"></a>
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

  
- `dict` - {
  Auroral indeces 'AL', 'AE', 'AO', 'AU' (int): {
- `'times'` _datetime.datetime_ - List of datetime objects
  corresponding to time in UT.
- `'values'` _int_ - List of indeces.
  }

<a name=".swmfpy.io.read_wdc_asy_sym"></a>
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

- `dict` - of values.
- `{'[ASY-SYM]-[D-H]'` - 'times': [], 'values': []}
  

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

<a name=".swmfpy.io.read_omni_csv"></a>
#### read\_omni\_csv

```python
read_omni_csv(filename, filtering=False, **kwargs)
```

Take an OMNI csv file from cdaweb.sci.gsfc.nasa.gov
and turn it into a pandas.DataFrame.

**Arguments**:

- `fnames` _dict_ - dict with filenames from omni .lst files.
  The keys must be: density, temperature,
  magnetic_field, velocity
- `filtering` _bool_ - default=False Remove points where the value
  is >sigma (default: sigma=3) from mean.
  **kwargs:
- `coarseness` _int_ - default=3, Number of standard deviations
  above which to remove if filtering=True.
- `clean` _bool_ - default=True, Clean the omni data of bad data points
  

**Returns**:

- `pandas.DataFrame` - object with solar wind data
  
  Make sure to download the csv files with cdaweb.sci.gsfc.nasa.gov
  the header seperated into a json file for safety.
  
  This only tested with OMNI data specifically.

<a name=".swmfpy.io.write_imf_input"></a>
#### write\_imf\_input

```python
write_imf_input(data, outfilename="IMF.dat", enable_rb=True, **kwargs)
```

Writes the pandas.DataFrame into an input file
that SWMF can read as input IMF (IMF.dat).

**Arguments**:

- `data` - pandas.DataFrame object with solar wind data
- `outfilename` - The output file name for ballistic solar wind data.
- `(default` - "IMF.dat")
- `enable_rb` - Enables solar wind input for the radiation belt model.
- `(default` - True)
  
  Other paramaters:
- `gse` - (default=False)
  Use GSE coordinate system for the file instead of GSM default.

<a name=".swmfpy.io.read_gm_log"></a>
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

  Dictionary of the log file
  

**Examples**:

  To plot AL and Dst get the log files
  ```python
  
  geo = swmfpy.io.read_gm_log('run/GM/IO2/geoindex_e20140215-100500.log')
  dst = swmfpy.io.read_gm_log('run/GM/IO2/log_e20140215-100500.log')
  
  # Plot AL indeces
  plt.plot(geo['times', geo['AL'])
  
  ```

<a name=".swmfpy.paramin"></a>
## swmfpy.paramin

These tools are to help script the editing of PARAM.in files.

<a name=".swmfpy.paramin.replace_command"></a>
#### replace\_command

```python
replace_command(parameters, input_file, output_file='PARAM.in')
```

Replace values for the parameters in a PARAM.in file.

Note, if you have repeat commands this will replace all the repeats.

**Arguments**:

- `parameters` _dict_ - Dictionary of strs with format
  replace = {'`COMMAND`': ['value', 'comments', ...]}
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
  
  change['`SOLARWINDFILE`'] = [['T', 'UseSolarWindFile'],
  ['new_imf.dat', 'NameSolarWindFile']]
  # This will overwrite PARAM.in
  swmfpy.paramin.replace('PARAM.in.template', change)
  
  ```

<a name=".swmfpy.paramin.read_command"></a>
#### read\_command

```python
read_command(command, paramin_file='PARAM.in', **kwargs)
```

Get parameters of a certain command in PARAM.in file.

This will find the `COMMAND` and return a list of values for the parameters.

**Arguments**:

- `command` _str_ - This is the `COMMAND` you're looking for.
- `paramin_file` _str_ - (default: 'PARAM.in') The file in which you're
  looking for the command values.
  **kwargs:
- `num_of_values` _int_ - (default: None) Number of values to take from
  command.
  

**Returns**:

- `list` - Values found for the `COMMAND` in file. Index 0 is `COMMAND` and
  the values follow (1 for first argument...)
  

**Raises**:

- `ValueError` - When the `COMMAND` is not found.
  

**Examples**:

  ```python
  
  start_time = swmfpy.paramin.read_command('`STARTTIME`')
  end_time = swmfpy.paramin.read_command('`ENDTIME`')
  print('Starting month is ', start_time[1])
  print('Ending month is ', end_time[1])
  
  ```
  
  This will treat all following lines as values for the command. To suppress
  this, try using the `num_of_values` keyword. This is helpful if your
  PARAM.in is comment heavy.

