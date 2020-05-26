"""### Editing PARAM.in files

These tools are to help script the editing and reading of PARAM.in files.
"""
__all__ = [
    'read_command',
    'replace_command'
    ]
__author__ = 'Qusai Al Shidi'
__email__ = 'qusai@umich.edu'

import logging
from .tools import _make_line


def replace_command(parameters, input_file, output_file='PARAM.in'):
    """Replace values for the parameters in a PARAM.in file.

    Note, if you have repeat commands this will replace all the repeats.

    Args:
        parameters (dict): Dictionary of strs with format
              replace = '\043COMMAND': ['value', 'comments', ...]
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
        change = {}
        change['\043SOLARWINDFILE'] = [['T', 'UseSolarWindFile'],
                                    ['new_imf.dat', 'NameSolarWindFile']]
        # This will overwrite PARAM.in
        swmfpy.paramin.replace('PARAM.in.template', change)
        ```
    """
    # Author: Qusai Al Shidi
    # Email: qusai@umich.edu

    logger = logging.getLogger()  # For debugging

    # Read and replace paramin file by making a temp list
    with open(input_file, 'rt') as paramin:

        # Compile lines in a list before editing/writing it
        lines = list(paramin)
        for line_num, line in enumerate(lines):

            # If the current command is what we want
            command = _get_command(line)
            if command in parameters.keys():

                for param, value in enumerate(parameters[command]):
                    newline = _make_line(value)
                    logger.info('Replacing: %s\n with: %s\n',
                                line, newline)
                    # Lines will be replaced in order
                    lines[line_num+param+1] = newline + '\n'

    # Write the PARAM.in file
    if output_file is not None:
        with open(output_file, 'w') as outfile:
            for line in lines:
                outfile.write(line)

    return lines


def read_command(command, paramin_file='PARAM.in', **kwargs):
    """Get parameters of a certain command in PARAM.in file.

    This will find the \043COMMAND and return a list of
    values for the parameters.

    Args:
        command (str): This is the \043COMMAND you're looking for.
        paramin_file (str): (default: 'PARAM.in') The file in which you're
                            looking for the command values.
        **kwargs:
            num_of_values (int): (default: None) Number of values to take from
                                 command.

    Returns:
        list: Values found for the \043COMMAND in file. Index 0 is
        \043COMMAND and the values follow (1 for first argument...)

    Raises:
        ValueError: When the \043COMMAND is not found.

    Examples:
        ```python
        start_time = swmfpy.paramin.read_command('\043STARTTIME')
        end_time = swmfpy.paramin.read_command('\043ENDTIME')
        print('Starting month is ', start_time[1])
        print('Ending month is ', end_time[1])
        ```

    This will treat all following lines as values for the command. To suppress
    this, try using the `num_of_values` keyword. This is helpful if your
    PARAM.in is comment heavy.
    """
    # Author: Qusai Al Shidi
    # Email: qusai@umich.edu

    logger = logging.getLogger()  # For debugging

    with open(paramin_file) as paramin:
        return_values = []
        command_found = False  # to know if worked
        in_command = False  # when after command needed
        for line in paramin:
            if _get_command(line) == command:
                logger.info('Found command: %s', command)
                command_found = True
                in_command = True
                return_values.append(command)
            elif in_command and _get_command(line):  # Make sure not out of cmd
                in_command = False
            elif line.split() and in_command:
                value = line.split()[0]
                logger.info('Value added: %s', value)
                return_values.append(value)

        # Error handling
        # Unable to find #COMMAND
        if not command_found:
            raise ValueError(command + ' not found.')

        # To ignore additional lines
        value_limit = kwargs.get('num_of_values', None)
        if value_limit:
            return_values = return_values[:value_limit+1]

        return return_values  # empty list might mean command not found


# HIDDEN FUNCTIONS
def _get_command(line):
    """Returns the '\043COMMAND' if on line.

    Args:
        line (str, list, tuple): The line in the PARAM.in file.

    Returns:
        (str): '\043COMMAND' if found and None if not.
    """
    if isinstance(line, (str, list, tuple)):  # Raises type error otherwise
        if isinstance(line, str):
            to_check = line.split()
            if to_check and to_check[0].startswith('#'):
                return to_check[0]
            return None
        return _get_command(line[0])
    return None
