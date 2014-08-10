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
    sys.stderr.write( 'ERROR: Configuration file (' + configName + ') is inaccessible.\n' )
    sys.stderr.write(e.strerror + '\n')
    sys.exit(1)
except ValidationError as e:
    sys.stderr.write( 'ERROR: Validation of configuration file (' + configName + ') failed.\n' )
    sys.stderr.write(e.details() + '\n')
    sys.exit(1)

for runs in simulationRunner.run_sessions( confDesc ):
    confDesc.get_output_writer( runs, confDesc.get_random_seed(), configName )()

    costIncrement = 10
    sessid = str(runs[0].get_session_id())
    
    figures.plotGainsAtRank( runs )
    figures.plotGainsAtCost(runs, costIncrement)
    figures.plotDerivedGains(runs, confDesc.get_derived_gains_dict( sessid ).iterkeys(), costIncrement)
    figures.plotCostsAtRank(runs)
    
    figures.plotCustomFigures(runs, confDesc.get_custom_figures_dict(sessid))
    