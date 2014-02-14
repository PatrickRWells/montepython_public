#!/usr/bin/python
"""
.. module:: MontePython
   :synopsis: Main module
.. moduleauthor:: Benjamin Audren <benjamin.audren@epfl.ch>

Monte Python, a Monte Carlo Markov Chain code (with Class!)
"""
import os
import sys
import warnings

# Checking for python version, comment if you are tired of seeing it when using
# a version < 2.7
VERSION = sys.version[:3]
if float(VERSION) < 2.7:
    print '\n\n /|\  You must have Python >= 2.7,'
    print '/_o_\ or install manually the following modules for your older'
    print '      distribution: argparse and OrderedDict'

import parser_mp   # parsing the input command line
import io_mp       # all the input/output mechanisms
import sampler     # generic sampler that calls different sampling algorithms
from data import Data  # data handling


def main(custom_command=''):
    """
    Main call of the function

    This function recovers the input from the command line arguments, from
    :mod:`parser_mp`, the parameter files.

    It then extracts the path of the used Monte Python code, assuming a
    standard setting (the data folder is in the same directory as the code
    folder).

    It finally proceeds to initialize a :class:`data` instance, a cosmological
    code instance, and runs the Markov chain.

    .. note::
        A possible parallelization would take place here.

    Parameters
    ----------
        custom_command: str
            allows for testing the code
    """
    # Parsing line argument
    command_line = parser_mp.parse(custom_command)

    # Default configuration
    path = {}

    # The path is recovered by taking the path to this file. By default, then,
    # the data folder is located in the same root directory. Any setting in the
    # configuration file will overwrite this one.
    path['root'] = os.path.sep.join(
        os.path.abspath(__file__).split(os.path.sep)[:-2])
    path['MontePython'] = os.path.join(path['root'], 'code')
    path['data'] = os.path.join(path['root'], 'data')

    # Configuration file, defaulting to default.conf in your root directory.
    # This can be changed with the command line option -conf. All changes will
    # be stored into the log.param of your folder, and hence will be reused for
    # an ulterior run in the same directory
    conf_file = os.path.abspath(command_line.config_file)
    if os.path.isfile(conf_file):
        for line in open(conf_file):
            exec(line)
        for key, value in path.iteritems():
            path[key] = os.path.normpath(value)
    else:
        raise io_mp.ConfigurationError(
            "You must provide a .conf file (default.conf by default in your" +
            " montepython directory that specifies the correct locations for" +
            " your data folder, Class (, Clik), etc...")

    # Recover Monte Python's version number
    with open(os.path.join(path['root'], 'VERSION'), 'r') as version_file:
        version = version_file.readline()

    sys.stdout.write('Running Monte Python v%s' % version)

    # If the info flag was used, read a potential chain (or set of chains) to
    # be analysed with default procedure. If the argument is a .info file, then
    # it will extract information from it (plots to compute, chains to analyse,
    # etc...)
    if command_line.files is not None:
        from analyze import analyze  # only invoked when analyzing
        analyze(command_line)
        return

    # Fill in data, starting from  parameter file. If output folder already
    # exists, the input parameter file was automatically replaced by the
    # existing log.param. This prevents you to run different things in a same
    # folder.
    else:
        data = Data(command_line, path)

    # Overwrite arguments from parameter file with the command line
    if command_line.N is None:
        try:
            command_line.N = data.N
        except AttributeError:
            raise io_mp.ConfigurationError(
                "You did not provide a number of steps, neither via " +
                "command line, nor in %s" % command_line.param)

    # Creating the file that will contain the chain, only with Metropolis
    # Hastings
    if command_line.method == 'MH':
        io_mp.create_output_files(command_line, data)

    # If there is a conflict between the log.param value and the .conf file,
    # exiting.
    if data.path != path:
        raise io_mp.ConfigurationError(
            "Your log.param file is in contradiction with your .conf file, " +
            "please check your path in these two places.")

    # Loading up the cosmological backbone. For the moment, only CLASS has been
    # wrapped.

    # Importing the python-wrapped CLASS from the correct folder, defined in
    # the .conf file, or overwritten at this point by the log.param.
    # If the cosmological code is CLASS, do the following to import all
    # relevant quantities
    if data.cosmological_module_name == 'CLASS':
        try:
            for elem in os.listdir(os.path.join(
                    data.path['cosmo'], os.path.join(
                    "python", "build"))):
                if elem.find("lib.") != -1:
                    classy_path = path['cosmo']+"python/build/"+elem
        except OSError:
            raise io_mp.ConfigurationError(
                "You probably did not compile the python wrapper of CLASS. " +
                "Please go to /path/to/class/python/ and do\n" +
                "..]$ python setup.py build")

        # Inserting the previously found path into the list of folders to
        # search for python modules.
        sys.path.insert(1, classy_path)
        try:
            from classy import Class
        except ImportError:
            raise io_mp.MissingLibraryError(
                "You must have compiled the classy.pyx file. Please go to " +
                "/path/to/class/python and run the command\n " +
                "python setup.py build")

        cosmo = Class()
    else:
        raise io_mp.ConfigurationError(
            "Unrecognised cosmological module. " +
            "Be sure to define the correct behaviour in MontePython.py " +
            "and data.py, to support a new one.")

    # Generic sampler call
    sampler.run(cosmo, data, command_line)

    # Closing up the file
    if command_line.method == 'MH':
        data.out.close()

#-----------------MAIN-CALL---------------------------------------------
if __name__ == '__main__':
    # Default action when facing a warning is being remapped to a custom one
    warnings.showwarning = io_mp.warning_message
    sys.exit(main())
