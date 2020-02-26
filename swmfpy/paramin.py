"""Tools to manipulate or create SWMF param.in files
"""

import logging


def replace(input_file, replace, output_file="PARAM.in"):
    """Replace values for the parameters in a PARAM.in file.

    Note, if you have repeat commands this will replace all the repeats.

    Args:
        input_file (str): String of PARAM.in file name.
        replace (dict): Dictionary of strs with format
                        replace = {"#COMMAND": ["value", "comments", ...]}
                        This is case sensitive.
        output_file (str): (default "PARAM.in") The output file to write to.
                           A value of None will not output a file.
    Returns:
        A list of lines of the PARAM.in file that would be outputted.

    Examples:
        ```
        change["#SOLARWINDFILE"] = [["T", "UseSolarWindFile"],
                                    ["new_imf.dat", "NameSolarWindFile"]]
        # This will overwrite PARAM.in
        swmfpy.paramin.replace("PARAM.in.template", change)
        ```
    """
    # TODO This will replace all for repeat commands.
    logger = logging.getLogger()  # For debugging
    # Read and replace paramin file by making a temp list
    with open(input_file, 'rt') as paramin:
        command = None  # Top level #COMMAND
        # Compile lines in a list before editing/writing it
        lines = list(paramin)
        for line_num, line in enumerate(lines):
            words = line.split()
            if words and words[0] in replace.keys():
                command = words[0]  # Current command
                for param, value in enumerate(replace[command]):
                    newline = ""
                    for text in value:
                        newline += text + "\t\t\t"
                    logger.info("Replacing:\n" + line
                                + "with:\n" + newline)
                    # Lines will be replaced in order
                    lines[line_num+param+1] = newline + '\n'
    # Write the PARAM.in file
    if output_file is None:
        return lines  # Break if None output_file (not default behaviour)
    with open(output_file, 'w') as outfile:
        for line in lines:
            outfile.write(line)
    return lines
