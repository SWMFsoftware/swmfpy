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
        verbose (bool): (Optional) Whether or not to print the equations as they are
            applied. Default behavior is silent.

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
            if line[0] == ' ':
                eqnstr = line.split("'")[1]
                tecplot.data.operate.execute_equation(eqnstr)
                if verbose:
                    print(eqnstr)
    if verbose:
        print('Successfully applied equations.')
