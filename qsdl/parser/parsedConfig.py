# -*- coding: latin-1 -*-
'''
Created on 5.10.2012

@author: Teemu P��kk�nen
'''

from qsdl.simulator import defaultCostCallbacks, defaultGainCallbacks, defaultConditionCallbacks, defaultProbabilityCallbacks
from qsdl.simulator import outputMapper
from qsdl.simulator import defaultDerivedGainsCallbacks
from qsdl.simulator import defaultDecays
from qsdl.parser import sessionReader
import qsdl.parser.cliParser as cliParser
import qsdl.parser.fileFormats as formats
from qsdl.simulator.errors.ConfigurationMissingError import ConfigurationMissingError
from qsdl.simulator.errors.ConfigurationInvalidError import ConfigurationInvalidError
import random
import sys
import callbackLoader
import itertools

def generate_range(start, stop, step):
    current = float(start)
    if isinstance(start, (int,long)) and isinstance(stop, (int,long)) and isinstance(step, (int,long)):
        current = int(start)

    while current < stop:
        yield current
        current += step

    yield stop


def get_probabilities_map(run):
    return dict([[probability.name, probability.value()] for probability in run.probability])

def get_callback_argument_variables_map(run):
    return dict([[arg.name, arg.value()] for arg in run.callback_argument])


def duplicate_run( run ):
    return sessionReader.Struct(
        probabilities = get_probabilities_map(run),
        callback_arguments = get_callback_argument_variables_map(run),
        id = run.id
    )


def generate_runs_for( run, run_map ):
    genrun_setup = run.generate

    generated_variables = []

    for cb_arg in genrun_setup.callback_argument:
        arg_steps = [sessionReader.Struct(name=cb_arg.name, type="callback_arguments", step=step) \
         for step in generate_range( cb_arg.range_start, cb_arg.range_end, cb_arg.step )]
        generated_variables.append( arg_steps )

    for prob in genrun_setup.probability:
        arg_steps = [sessionReader.Struct(name=prob.name, type="probabilities", step=step) \
         for step in generate_range( prob.range_start, prob.range_end, prob.step )]
        generated_variables.append( arg_steps )

    for combination in itertools.product( *generated_variables ):
        generated_run = duplicate_run( run )
        generated_id = str( generated_run.id )
        for gen_var in combination:
            target_dict = getattr(generated_run, gen_var.type)
            target_dict[ gen_var.name ] = gen_var.step
            generated_id += '-' + str(gen_var.name)[:10] + '-' + str(gen_var.step)
        run_map[ generated_id ] = generated_run


class ConfigDescriptor(object):
    '''
    classdocs
    '''


    def __init__(self, pyxbConfig):
        '''
        Constructor
        '''

        self.doc = pyxbConfig

        def get_gains_map( gainsElement ):
            return dict( [ [ gain.relevance_level, gain.gain ] for gain in gainsElement.gain ] )

        def get_session_map():
            map_ = None
            if self.sessions_directory_is_given():
                map_ = sessionReader.read_sessions_from_directory(
                    self.get_input_directory(), self.get_sessions_directory_name() )
            else:
                map_ = {}
                for session in self.doc.sessions.session:
                    if hasattr( session, 'gains' ):
                        session.gainsMap = get_gains_map( session.gains )
                    map_[ session.id ] = session
            return map_

        def get_run_map():
            map_ = {}
            if not hasattr(self.doc, 'runs') or self.doc.runs is None:
                map_['default'] = {}
                return map_
            for run in self.doc.runs.run:
                if run.generate is not None:
                    generate_runs_for( run, map_ )
                else:
                    run.probabilities = get_probabilities_map(run)
                    run.callback_arguments = get_callback_argument_variables_map(run)
                    map_[run.id] = run
            return map_

        self.defaultGains = get_gains_map( self.doc.defaults.gains )
        self.defaultGains = dict(
            [ [ gain.relevance_level, gain.gain ] for gain in self.doc.defaults.gains.gain ] )
        self.sessions = get_session_map()
        self.runs = get_run_map()

        # Relevances

        def get_relevance_reader_generator_for( relFile ):
            return formats.get_relevance_reader_generator( relFile.format )

        def get_relevance_file_reader_for( relFile ):
            return get_relevance_reader_generator_for( relFile )(
                self.get_input_directory() + relFile.value() )

        def get_relevances_for( relFile ):
            reader = get_relevance_file_reader_for( relFile )
            if not reader['can_parse']():
                raise ConfigurationInvalidError("Relevance file (%s) cannot be parsed. Check format." % relFile.value())
            return reader['get_relevances']()

        def get_relevances():
            return [ get_relevances_for( relFile ) for relFile in self.doc.files.relevance_file ]

        self.relevances = {}
        for rels in get_relevances():
            self.relevances.update( rels )

    def get_variable_probability_value(self, runId, variableName):
        run = self.runs[runId]
        return run.probabilities[variableName]

    def get_sessions_directory_name(self):
        return self.doc.sessions.sessions_directory.strip()

    def get_variable_callback_arguments(self, runId):
        run = self.runs[runId]
        if hasattr(run, 'callback_arguments'):
            return run.callback_arguments
        return None

    def get_run_id_iterator(self):
        return self.runs.iterkeys()

    def get_gain(self, sessionId, documentRelevanceLevel):
        session = self.get_session(sessionId)
        if hasattr( session, 'gains' ):
            return session.gainsMap[ documentRelevanceLevel ]

        return self.defaultGains[ str(documentRelevanceLevel) ]

    def get_input_directory(self):
        return (self.doc.files.input_directory or '.') + '/'

    # def get_sessions_directory(self):
    #     if self.doc.sessions.sessions_directory is not None:
    #         return self.get_input_directory() + self.doc.sessions.sessions_directory + '/'
    #     else
    #         return self.get_input_directory()

    def get_page_size(self, sessionId):
        session = self.get_session(sessionId)
        if hasattr( session, 'page_size' ) and session.page_size != None:
            return int(session.page_size)

        try:
            return int(self.doc.defaults.page_size)
        except TypeError:
            raise ConfigurationMissingError( 'Page size missing for session id ' + sessionId )

    def get_random_seed(self):
        '''
        Returns a random seed for initializing the random number generator.
        If a seed is defined in the configuration file, it is returned;
        otherwise a randomly generated seed is returned.
        If a seed has already been generated previously, it is returned.
        '''
        if not hasattr( self, 'randomSeed' ):
            options = self.doc.options
            if hasattr( options, 'random_seed' ) and options.random_seed != None:
                self.randomSeed = int( options.random_seed )
            else:
                self.randomSeed = random.randint(0, sys.maxint)
        return self.randomSeed

    def get_session(self, sessId):
        return self.sessions[ sessId ]

    def get_session_id_iterator(self):
        return self.sessions.iterkeys()

    def get_initial_session_id(self):
        return self.doc.sessions.session[0].id

    def get_cost_callbacks_module_name(self):
        if hasattr(self.doc.files, 'cost_callbacks') and \
        self.doc.files.cost_callbacks != None:
            return self.doc.files.cost_callbacks.rsplit( '.', 1 )[ 0 ]
        return 'customCostCallbacks'

    def get_cost_callbacks(self):
        if not hasattr( self, 'costCallbacks' ):
            customCallbacks = callbackLoader.get_callback_module(
                            self.get_cost_callbacks_module_name() )
            if customCallbacks is not None:
                cbMap = defaultCostCallbacks.get_callback_map().copy()
                cbMap.update( customCallbacks.get_callback_map() )
                self.costCallbacks = cbMap
            else:
                self.costCallbacks = defaultCostCallbacks.get_callback_map()
        return self.costCallbacks

    def get_decay_callbacks_module_name(self):
        if hasattr(self.doc.files, 'decay_callbacks') and \
        self.doc.files.decay_callbacks != None:
            return self.doc.files.decay_callbacks.rsplit( '.', 1 )[ 0 ]
        return 'customDecayCallbacks'

    def get_decays(self):
        if not hasattr( self, 'decays' ):
            customCallbacks = callbackLoader.get_callback_module(
                            self.get_decay_callbacks_module_name() )
            if customCallbacks != None:
                cbMap = defaultDecays.get_callback_map().copy()
                cbMap.update( customCallbacks.get_callback_map() )
                self.decays = cbMap
            else:
                self.decays = defaultDecays.get_callback_map()
        return self.decays

    def get_gain_callbacks_module_name(self):
        if hasattr(self.doc.files, 'gain_callbacks') and \
        self.doc.files.gain_callbacks != None:
            return self.doc.files.gain_callbacks.rsplit( '.', 1 )[ 0 ]
        return 'customGainCallbacks'

    def get_gain_callbacks(self):
        if not hasattr( self, 'gainCallbacks' ):
            customCallbacks = callbackLoader.get_callback_module(
                            self.get_gain_callbacks_module_name() )
            if customCallbacks != None:
                cbMap = defaultGainCallbacks.get_callback_map().copy()
                cbMap.update( customCallbacks.get_callback_map() )
                self.gainCallbacks = cbMap
            else:
                self.gainCallbacks = defaultGainCallbacks.get_callback_map()
        return self.gainCallbacks

    def get_condition_callbacks_module_name(self):
        if hasattr(self.doc.files, 'condition_callbacks') and \
        self.doc.files.condition_callbacks != None:
            return self.doc.files.condition_callbacks.rsplit( '.', 1 )[ 0 ]
        return 'customConditionCallbacks'

    def get_condition_callbacks(self):
        if not hasattr( self, 'conditionCallbacks' ):
            customCallbacks = callbackLoader.get_callback_module(
                        self.get_condition_callbacks_module_name() )
            if customCallbacks != None:
                cbMap = defaultConditionCallbacks.get_callback_map().copy()
                cbMap.update( customCallbacks.get_callback_map() )
                self.conditionCallbacks = cbMap
            else:
                self.conditionCallbacks = defaultConditionCallbacks.get_callback_map()
        return self.conditionCallbacks

    def get_probability_callbacks(self):
        if not hasattr(self, 'probabilityCallbacks'):
            customCallbacks = callbackLoader.get_callback_module(
                self.get_probability_callbacks_module_name())
            if customCallbacks is not None:
                cbMap = defaultProbabilityCallbacks.get_callback_map().copy()
                cbMap.update(customCallbacks.get_callback_map())
                self.probabilityCallbacks = cbMap
            else:
                self.probabilityCallbacks = defaultProbabilityCallbacks.get_callback_map()
        return self.probabilityCallbacks

    def get_probability_callbacks_module_name(self):
        if hasattr(self.doc.files, 'probability_callbacks') and \
           self.doc.files.probability_callbacks is not None:
                return self.doc.files.probability_callbacks.rsplit('.', 1)[0]
        return 'customProbabilityCallbacks'

    def get_simulation_file(self):
        return file( self.get_input_directory() + self.doc.files.simulation )

    def get_reader(self, sessionId):
        '''
        Creates a data reader for a specific session
        '''
        session = self.get_session( sessionId )
        return sessionReader.get_session_reader(session, self)

    def sessions_directory_is_given(self):
        return hasattr( self.doc.sessions, 'sessions_directory' ) and \
            self.doc.sessions.sessions_directory is not None

    def get_override_output_directory(self):
        return cliParser.get_output_directory()

    def get_cross_session_output_directory(self):
        overrideDir = self.get_override_output_directory()
        if overrideDir is not None:
            return overrideDir

        if self.sessions_directory_is_given():
            return self.get_input_directory() + self.get_sessions_directory_name()
        return '.'

    def get_output_directory(self, sessionId):
        overrideDir = self.get_override_output_directory()
        if overrideDir is not None:
            return overrideDir

        directory = '.'
        session = self.get_session( sessionId )
        if hasattr( session.output, 'directory' ) and session.output.directory is not None:
            directory = session.output.directory
        return directory

    def get_output_file(self, sessionId, fileMode, runId):
        session = self.get_session( sessionId )
        if hasattr( session.output, 'file' ) and session.output.file != None:
            return file( self.get_output_directory(sessionId) + '/' + runId + '_' + session.output.file, fileMode )
        return sys.stdout # default: write to stdout

    def get_cross_session_output_file(self, fileMode, runId):
        return file( self.get_cross_session_output_directory() + '/' + runId + '_X-session.out', fileMode )

    def get_output_format(self, sessionId):
        session = self.get_session(sessionId)
        if hasattr( session.output, 'format' ) and session.output.format != None:
            return session.output.format
        return self.doc.defaults.output.format

    def get_cross_session_output_format(self):
        return self.doc.defaults.output.format

    def get_output_formatter(self, sessId):
        format_ = self.get_output_format(sessId)
        return outputMapper.get_output_formatters()[ format_ ]( self, sessId )

    def get_cross_session_output_formatter(self):
        format_ = self.get_cross_session_output_format()
        return outputMapper.get_cross_session_output_formatters()[ format_ ]( self )

    def get_relevance_level(self, topic, docid):
        try:
            (qid, docid_, rlevel) = self.relevances[ topic ][ docid ]
            return rlevel
        except KeyError:
            if self.doc.options.ignore_missing_relevance_data:
                return self.doc.options.missing_relevance_level
            raise

    def get_default_query_file_format(self):
        return self.doc.defaults.sessions.query_file_format

    def get_default_result_file_format(self):
        return self.doc.defaults.sessions.result_file_format

    def get_iterations(self, sessionId):
        session = self.get_session(sessionId)
        try:
            if hasattr( session, 'iterations' ) and session.iterations != None:
                return int(session.iterations)
            return int(self.doc.defaults.iterations)
        except TypeError:
            raise ConfigurationMissingError( \
                'Number of iterations missing for session id ' + str(session.id) )

    def get_output_writer(self, runs, seed, configFileName, runId):

        # File writer
        def write():
            firstRun = runs[0]
            sessId = firstRun.get_session_id()
            formatter = self.get_output_formatter( sessId )
            file_ = self.get_output_file(sessId, formatter['get_file_mode'](), runId)
            file_.write( formatter[ 'set_up' ]() + '\n' )
            file_.write( formatter[ 'format_history' ]( runs ) + '\n' )
            file_.write( formatter[ 'format_stats' ]( runs ) + '\n' )
            file_.write( formatter[ 'format_seed' ]( seed ) + '\n' )
            file_.write( formatter[ 'format_input_files' ]( configFileName, self.doc.files.simulation ) + '\n' )

        return write

    def get_cross_session_output_writer(self, sessions, runId):

        # File writer
        def write():
            formatter = self.get_cross_session_output_formatter()
            file_ = self.get_cross_session_output_file(formatter['get_file_mode'](), runId)
            file_.write( formatter[ 'format_cross_session_stats' ]( sessions ) + '\n' )

        return write

    def get_verbose_writer(self):
        if self.doc.options.verbose_output:
            def write( textReturningFunction ): print textReturningFunction()
            return write
        def noopWrite( textReturningFunction ): pass
        return noopWrite

    def get_initial_derived_gain_values_dict(self, sessionId):
        session = self.get_session(sessionId)
        if not hasattr( session, 'initialDerivedGainsValues' ):
            session.initialDerivedGainsValues = dict( [ (gaintypeId, 0.) for gaintypeId \
                                in self.get_derived_gains_dict( sessionId ).iterkeys() ] )
        return session.initialDerivedGainsValues

    def get_default_custom_figures_dict(self):
        if not hasattr( self, 'defaultCustomFigures' ):
            if hasattr( self.doc.defaults.output, 'figures' ) and \
                self.doc.defaults.output.figures != None:
                    self.defaultCustomFigures = dict( [(figure.id, figure) for figure in \
                                  self.doc.defaults.output.figures.custom_figure] )
            else:
                self.defaultCustomFigures = {}
        return self.defaultCustomFigures

    def get_custom_figures_dict(self, sessionId):
        session = self.get_session(sessionId)
        if not hasattr( session, 'customFigures' ):
            session.customFigures = self.get_default_custom_figures_dict().copy()
            if hasattr( session.output, 'figures' ) and session.output.figures != None:
                session.customFigures.update( dict( [ (figure.id, figure) for figure \
                                         in session.output.figures.custom_figure ] ) )
        return session.customFigures

    def get_default_derived_gains_dict(self):
        if not hasattr( self, 'defaultDerivedGains' ):
            if hasattr( self.doc.defaults.output, 'gain_types' ) and \
                self.doc.defaults.output.gain_types != None:
                    self.defaultDerivedGains = dict( [(gaintype.id, gaintype) for gaintype in \
                                  self.doc.defaults.output.gain_types.type] )
            else:
                self.defaultDerivedGains = {}
        return self.defaultDerivedGains

    def get_derived_gains_dict(self, sessionId):
        session = self.get_session(sessionId)
        if not hasattr( session, 'derivedGains' ):
            session.derivedGains = self.get_default_derived_gains_dict().copy()
            if hasattr( session.output, 'gain_types' ) and session.output.gain_types != None:
                session.derivedGains.update( dict( [ (gaintype.id, gaintype) for gaintype \
                                         in session.output.gain_types.type ] ) )
        return session.derivedGains

    def get_derived_gains_callbacks_dict(self, sessionId):
        session = self.get_session(sessionId)
        if not hasattr( session, 'derivedGainsCallbacksDict' ):
            session.derivedGainsCallbacksDict = dict( [ (gaintype.id, gaintype.function) for gaintype \
                                in self.get_derived_gains_dict( sessionId ).itervalues() ] )
        return session.derivedGainsCallbacksDict

    def get_derived_gains_callbacks_module_name(self):
        if hasattr(self.doc.files, 'derived_gains_callbacks') and \
        self.doc.files.derived_gains_callbacks != None:
            return self.doc.files.derived_gains_callbacks.rsplit( '.', 1 )[ 0 ]
        return 'customDerivedGainsCallbacks'

    def get_derived_gains_callbacks(self):
        if not hasattr( self, 'derivedGainsCallbacks' ):
            customCallbacks = callbackLoader.get_callback_module(
                            self.get_derived_gains_callbacks_module_name() )
            if customCallbacks != None:
                cbMap = defaultDerivedGainsCallbacks.get_callback_map().copy()
                cbMap.update( customCallbacks.get_callback_map() )
                self.derivedGainsCallbacks = cbMap
            else:
                self.derivedGainsCallbacks = defaultDerivedGainsCallbacks.get_callback_map()

        return self.derivedGainsCallbacks

    def get_trigger_callbacks_module_name(self):
        if hasattr(self.doc.files, 'trigger_callbacks') and \
        self.doc.files.trigger_callbacks != None:
            return self.doc.files.trigger_callbacks.rsplit( '.', 1 )[ 0 ]
        return 'customTriggerCallbacks'

    def only_cross_session_output(self):
        if hasattr( self.doc, 'options') and hasattr( self.doc.options, 'only_x_session' ):
            return self.doc.options.only_x_session
        return False

