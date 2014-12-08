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


def plot_cross_session_figures( sessions, costIncrement, gainIds ):
    figures.plotAverageGainsAtRankAcrossSessions( sessions )
    figures.plotAverageGainsAtCostAcrossSessions( sessions, costIncrement )
    figures.plotDerivedGainsAcrossSessions( sessions, gainIds, costIncrement )


DEFAULT_COST_INCREMENT = 10

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
        sessions = simulationRunner.run_sessions( confDesc, runId )

        confDesc.get_cross_session_output_writer( sessions, runId )()

        figures.set_output_directory( confDesc.get_cross_session_output_directory() )
        plot_cross_session_figures( sessions, DEFAULT_COST_INCREMENT, confDesc.get_default_derived_gains_dict().keys() )

        if not confDesc.only_cross_session_output():
            for simulationIterations in sessions:
                confDesc.get_output_writer( simulationIterations, confDesc.get_random_seed(), configName, runId )()

                sessid = str(simulationIterations[0].get_session_id())

                figures.set_output_directory( confDesc.get_output_directory( sessid ) )

                figures.plotGainsAtRank( simulationIterations )
                figures.plotGainsAtCost(simulationIterations, DEFAULT_COST_INCREMENT)
                figures.plotDerivedGains(simulationIterations, confDesc.get_derived_gains_dict( sessid ).iterkeys(), DEFAULT_COST_INCREMENT)
                figures.plotCostsAtRank(simulationIterations)

                figures.plotCustomFigures(simulationIterations, confDesc.get_custom_figures_dict(sessid))

except ValidationError as e:
    sys.stderr.write( 'ERROR: Invalid content found in simulation description.\n' )
    sys.stderr.write(e.details() + '\n')
    sys.exit(1)
