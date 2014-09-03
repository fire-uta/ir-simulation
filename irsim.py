import sys
from pyxb.exceptions_ import ValidationError
import qsdl.parser.config01 as configPYXB
from qsdl.parser.parsedConfig import ConfigDescriptor
import qsdl.simulator.simulationRunner as simulationRunner
import qsdl.parser.cliParser as cliParser
import matplotlib as matplotlib
# Use a non-interactive matplotlib backend to allow running in command line env.
matplotlib.use('AGG')
import figures as figures

configName = cliParser.get_config_file_name()
confDesc = None
try:
    confDesc = ConfigDescriptor( configPYXB.CreateFromDocument(
                    file(configName).read()) )
except IOError as e:
    sys.stderr.write( 'ERROR: Configuration file or a file referenced in the config is inaccessible.\n' )
    sys.stderr.write(e.strerror + ' - ' + e.filename + '\n')
    sys.exit(1)
except ValidationError as e:
    sys.stderr.write( 'ERROR: Validation of configuration file (' + configName + ') failed.\n' )
    sys.stderr.write(e.details() + '\n')
    sys.exit(1)

try:
    for runId in confDesc.get_run_id_iterator():
        figures.set_run_id(runId)
        for simulationIterations in simulationRunner.run_sessions( confDesc, runId ):
            confDesc.get_output_writer( simulationIterations, confDesc.get_random_seed(), configName, runId )()

            costIncrement = 10
            sessid = str(simulationIterations[0].get_session_id())

            #FIXME: figures module should derive filenames from runId
            figures.plotGainsAtRank( simulationIterations )
            figures.plotGainsAtCost(simulationIterations, costIncrement)
            figures.plotDerivedGains(simulationIterations, confDesc.get_derived_gains_dict( sessid ).iterkeys(), costIncrement)
            figures.plotCostsAtRank(simulationIterations)

            figures.plotCustomFigures(simulationIterations, confDesc.get_custom_figures_dict(sessid))

except ValidationError as e:
    sys.stderr.write( 'ERROR: Invalid content found in simulation description.\n' )
    sys.stderr.write(e.details() + '\n')
    sys.exit(1)

