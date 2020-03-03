"""Tools to manipulate or create param.in files

PARAM.in Tools
==============

These tools are to help script the editing of PARAM.in files.
"""
__all__ = ['read_command', 'replace_command']
__author__ = 'Qusai Al Shidi'
__email__ = 'qusai@umich.edu'

import logging


def replace_command(parameters, input_file, output_file='PARAM.in'):
    """Replace values for the parameters in a PARAM.in file.

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

    Examples:
        ```
        change['#SOLARWINDFILE'] = [['T', 'UseSolarWindFile'],
                                    ['new_imf.dat', 'NameSolarWindFile']]
        # This will overwrite PARAM.in
        swmfpy.paramin.replace('PARAM.in.template', change)
        ```
    """
    # Author: Qusai Al Shidi
    # Email: qusai@umich.edu

    # TODO This will replace all for repeat commands.
    logger = logging.getLogger()  # For debugging

    # Read and replace paramin file by making a temp list
    with open(input_file, 'rt') as paramin:
        command = None  # Current command
        # Compile lines in a list before editing/writing it
        lines = list(paramin)
        for line_num, line in enumerate(lines):
            words = line.split()

            # If the current command is what we want
            if words and words[0] in parameters.keys():
                command = words[0]

                # Replace code
                for param, value in enumerate(parameters[command]):
                    newline = ''
                    # Allow additions of comments if list(str)
                    if isinstance(value, list):
                        for text in value:
                            newline += text + '\t\t\t'
                        logger.info('Replacing: %s\n with: %s\n',
                                    line, newline)
                        # Lines will be replaced in order
                        lines[line_num+param+1] = newline + '\n'
                    # Else just make a line
                    elif isinstance(value, str):
                        logger.info('Replacing: %s\n with: %s\n', line, value)
                        # Lines will be replaced in order
                        lines[line_num+param+1] = value + '\n'

    # Write the PARAM.in file
    if output_file is None:
        return lines  # Break if None output_file (not default behaviour)
    with open(output_file, 'w') as outfile:
        for line in lines:
            outfile.write(line)

    return lines


def read_command(command, paramin_file='PARAM.in', **kwargs):
    """Get parameters of a certain command in PARAM.in file.

    This will find the #COMMAND and return a list of values for the parameters.

    Args:
        command (str): This is the #COMMAND you're looking for.
        paramin_file (str): (default: 'PARAM.in') The file in which you're
                            looking for the command values.
        **kwargs:
            num_of_values (int): (default: None) Number of values to take from
                                 command.

    Returns:
        list: Values found for the #COMMAND in file. Index 0 is #COMMAND and
              the values follow (1 for first argument...)

    Raises:
        ValueError: When the #COMMAND is not found.

    Examples:
        start_time = swmfpy.paramin.read_command('#STARTTIME')
        end_time = swmfpy.paramin.read_command('#ENDTIME')
        print('Starting month is ', start_time[1])
        print('Ending month is ', end_time[1])

    This will treat all following lines as values for the command. To suppress
    this, try using the `num_of_values` keyword. This is helpful if your
    PARAM.in is comment heavy.
    """
    # Author: Qusai Al Shidi
    # Email: qusai@umich.edu

    logger = logging.getLogger()  # For debugging

    with open(paramin_file) as paramin:
        return_values = []
        found_command = False  # to know if worked
        at_command = False  # when after command needed
        for line in paramin:
            words = line.split()
            if words and words[0] == command:
                logger.info('Found command: %s', command)
                found_command = True
                at_command = True
                return_values.append(command)
            elif words and words[0][0] == '#':
                at_command = False
            elif words and at_command:
                value = words[0]
                logger.info('Value added: %s', value)
                return_values.append(value)

        # Error handling
        # Unable to find #COMMAND
        if not found_command:
            raise ValueError(command + ' not found.')

        # To ignore additional lines
        value_limit = kwargs.get('num_of_values', None)
        if value_limit:
            return_values = return_values[:value_limit+1]

        return return_values  # empty list might mean command not found
