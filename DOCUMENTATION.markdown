
# swmfpy

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


# swmfpy.io
Input/Output tools

Input/Output
============

Here are tools to read and write files relating to SWMF.

TODO: Move pandas dependancy elsewhere.


## read_wdc_ae
```python
read_wdc_ae(wdc_filename)
```
Read an auroral electrojet (AE) indeces from Kyoto's World Data Center
text file into a dictionary of lists.

Args:
 wdc_filename (str): Filename of wdc data from
                     http://wdc.kugi.kyoto-u.ac.jp/
Returns:
 dict: {
        Auroral indeces 'AL', 'AE', 'AO', 'AU' (int): {
             'times' (datetime.datetime): List of datetime objects
                                          corresponding to time in UT.
             'values' (int): List of indeces.
       }


## read_wdc_asy_sym
```python
read_wdc_asy_sym(wdc_filename)
```
Reads a WDC file for ASY/SYM data.

Reads an ASY/SYM file downloaded from
http://wdc.kugi.kyoto-u.ac.jp/aeasy/index.html
and puts it into a dictionary.

Args:
    wdc_filename (str): Relative filename (or file handle no.) to read.

Returns:
    dict: of values.
    {'[ASY-SYM]-[D-H]': 'times': [], 'values': []}

Examples:
    ```
    indeces = swmfpy.io.read_wdc_asy_sym('wdc.dat')
    # Plot data
    plt.plot(indeces['SYM-H']['times'],
             indeces['SYM-H']['values'],
             label='SYM-H [nT]'
             )
    plt.xlabel('Time [UT]')
    ```

Important to note if there is bad data it will be filled as None.


## read_omni_csv
```python
read_omni_csv(filename, filtering=False, **kwargs)
```
Take an OMNI csv file from cdaweb.sci.gsfc.nasa.gov
and turn it into a pandas.DataFrame.

Args:
    fnames (dict): dict with filenames from omni .lst files.
                   The keys must be: density, temperature,
                                     magnetic_field, velocity
    filtering (bool): default=False Remove points where the value
                      is >sigma (default: sigma=3) from mean.
    **kwargs:
        coarseness (int): default=3, Number of standard deviations
                          above which to remove if filtering=True.
        clean (bool): default=True, Clean the omni data of bad data points

Returns:
    pandas.DataFrame: object with solar wind data

Make sure to download the csv files with cdaweb.sci.gsfc.nasa.gov
the header seperated into a json file for safety.

This only tested with OMNI data specifically.


## write_imf_input
```python
write_imf_input(data, outfilename='IMF.dat', enable_rb=True, **kwargs)
```
Writes the pandas.DataFrame into an input file
that SWMF can read as input IMF (IMF.dat).

Args:
    data: pandas.DataFrame object with solar wind data
    outfilename: The output file name for ballistic solar wind data.
                 (default: "IMF.dat")
    enable_rb: Enables solar wind input for the radiation belt model.
               (default: True)

Other paramaters:
    gse: (default=False)
        Use GSE coordinate system for the file instead of GSM default.


## read_gm_log
```python
read_gm_log(filename, colnames=None, dtypes=None, index_time=True)
```
Make a dictionary out of the indeces outputted
from the GM model log.

Args:
    filename (str): The relative filename as a string. (or file handle no.)
    colnames ([str]): (default: None) Supply the name of the columns.
                                      If None it will use second line
                                      of log file.
    dtypes ([types]): (default: None) Provide types for the columns, if
                                      None then all will be float.
    index_time (bool): (default: True) Make a column of dt.datetime objects
                                       in dictionary key 'Time [UT]'.

Returns:
    Dictionary of the log file

Examples:
    To plot AL and Dst get the log files
    ```
    geo = swmfpy.io.read_gm_log('run/GM/IO2/geoindex_e20140215-100500.log')
    dst = swmfpy.io.read_gm_log('run/GM/IO2/log_e20140215-100500.log')

    # Plot AL indeces
    plt.plot(geo['times', geo['AL'])
    ```



# swmfpy.paramin

PARAM.in Tools
--------------

These tools are to help script the editing of PARAM.in files.


## replace_command
```python
replace_command(parameters, input_file, output_file='PARAM.in')
```
Replace values for the parameters in a PARAM.in file.

Note, if you have repeat commands this will replace all the repeats.

Args:
    parameters (dict): Dictionary of strs with format
                    replace = {'#COMMAND': ['value', 'comments', ...]}
                    This is case sensitive.
    input_file (str): String of PARAM.in file name.
    output_file (str): (default 'PARAM.in') The output file to write to.
                       A value of None will not output a file.
Returns:
    A list of lines of the PARAM.in file that would be outputted.

Raises:
    TypeError: If a value given couldn't be converted to string.

Examples:
    ```python

    change['#SOLARWINDFILE'] = [['T', 'UseSolarWindFile'],
                                ['new_imf.dat', 'NameSolarWindFile']]
    # This will overwrite PARAM.in
    swmfpy.paramin.replace('PARAM.in.template', change)

    ```


## read_command
```python
read_command(command, paramin_file='PARAM.in', **kwargs)
```
Get parameters of a certain command in PARAM.in file.

This will find the [`COMMAND`](#COMMAND) and return a list of values for the parameters.

Args:
    command (str): This is the [`COMMAND`](#COMMAND) you're looking for.
    paramin_file (str): (default: 'PARAM.in') The file in which you're
                        looking for the command values.
    **kwargs:
        num_of_values (int): (default: None) Number of values to take from
                             command.

Returns:
    list: Values found for the [`COMMAND`](#COMMAND) in file. Index 0 is [`COMMAND`](#COMMAND) and
          the values follow (1 for first argument...)

Raises:
    ValueError: When the [`COMMAND`](#COMMAND) is not found.

Examples:
    ```python

    start_time = swmfpy.paramin.read_command('#STARTTIME')
    end_time = swmfpy.paramin.read_command('#ENDTIME')
    print('Starting month is ', start_time[1])
    print('Ending month is ', end_time[1])

    ```

This will treat all following lines as values for the command. To suppress
this, try using the `num_of_values` keyword. This is helpful if your
PARAM.in is comment heavy.


# swmfpy.web
Tools to retrieve and send data on the web.

SWMF Web Tools
==============

Here are a collection of tools to work with data on the internet. Thus,
this module mostly requires an internet connection.


## get_omni_data
```python
get_omni_data(time_from, time_to, **kwargs)
```
Retrieve omni solar wind data over http.

This will download omni data from https://spdf.gsfc.nasa.gov/pub/data/omni
and put it into a dictionary. If your data is large, then make a csv and
use swmfpy.io.read_omni_data().

Args:
    time_from (datetime.datetime): The start time of the solar wind
                                   data that you want to receive.
    time_to (datetime.datetime): The end time of the solar wind data
                                 you want to receive.

Returns:
    dict: This will be a list of *all* columns
          available in the omni data set.

Examples:
    ```python

    import datetime
    import swmfpy.web

    storm_start = datetime.datetime(year=2000, month=1, day=1)
    storm_end = datetime.datetime(year=2000, month=2, day=15)
    data = swmfpy.web.get_omni_data(time_from=storm_start,
                                    time_to=storm_end)
    ```


## download_magnetogram_adapt
```python
download_magnetogram_adapt(time, map_type='fixed', **kwargs)
```
This routine downloads GONG ADAPT magnetograms.

Downloads ADAPT magnetograms from ftp://gong2.nso.edu/adapt/maps/gong/
to a local directory. It will download all maps with the regex file
pattern: adapt4[0,1]3*yyyymmddhh

Args:
    time (datetime.datetime): Time in which you want the magnetogram.
    map_type (str): (default: 'fixed')
                    Choose either 'fixed' or 'central' for
                    the map type you want.
    **kwargs:
        download_dir (str): (default is current dir) Relative directory
                            where you want the maps to be downloaded.

Returns:
    str: First unzipped filename found.

Raises:
    NotADirectoryError: If the adapt maps directory
                        is not found on the server.
    ValueError: If map_type is not recognized.
                (i.e. not 'fixed' or 'central')
    FileNotFoundError: If maps were not found.

Examples:
    ```python

    import datetime as dt

    # Use datetime objects for the time
    time_flare = dt.datetime(2018, 2, 12, hour=10)
    swmfpy.web.download_magnetogram_adapt(time=time_flare,
                                          map_type='central',
                                          download_dir='./mymaps/')
    ```

