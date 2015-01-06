# -*- coding: latin-1 -*-
'''
Created on 19.10.2012

@author: Teemu Pääkkönen
'''

import os
import re
import qsdl.parser.fileFormats as formats

from qsdl.simulator.errors.TriggerError import TriggerError

from operator import attrgetter
from collections import OrderedDict

class SessionReaderState: pass
SessionReaderState.currentQRPairIndex = None
SessionReaderState.currentQRPairQueryIndex = None

class Struct:
    def __init__(self, **entries): self.__dict__.update(entries)

    def __repr__(self, *args, **kwargs):
        return repr( self.__dict__ )

queryFilePattern = re.compile('^([^_]+)_q(\d+)$')

def handle_query_file_name_match( session_map, queryFileNameMatch, session_directory, input_directory ):
    query_file_name = queryFileNameMatch.group(0)
    session_id = queryFileNameMatch.group(1)
    query_number = queryFileNameMatch.group(2)
    expected_result_file_name = query_file_name + 'r'

    if session_id not in session_map:
        session_map[ session_id ] = Struct(
            id = session_id,
            use_queries = [],
            output = Struct(
                file = session_id + '.out',
                directory = input_directory + session_directory
            )
        )

    use_queries = Struct(
        query_file = session_directory + '/' + query_file_name,
        result_file = session_directory + '/' + expected_result_file_name,
        query_file_format = None,
        topics = None,
        result_file_format = None
    )
    session_map[ session_id ].use_queries.append( use_queries )


def sort_session_map( unsorted_session_map ):
    for session in unsorted_session_map.itervalues():
        session.use_queries = sorted(session.use_queries, key=attrgetter('query_file'))
    return unsorted_session_map


def read_sessions_from_directory( input_directory, sessions_directory ):
    session_map = OrderedDict()

    directory = input_directory + sessions_directory
    for dirname, dirnames, filenames in os.walk( directory ):
        for filename in filenames:
            queryFileNameMatch = queryFilePattern.match( filename )
            if queryFileNameMatch is not None:
                handle_query_file_name_match( session_map, queryFileNameMatch, sessions_directory, input_directory )

    session_map = sort_session_map( session_map )
    return session_map

def get_session_reader( session, config ):

    qrPairs = []

    for useQueries in session.use_queries:
        queryFileName = config.get_input_directory() + useQueries.query_file
        queryFileFormat = useQueries.query_file_format or config.get_default_query_file_format()
        queryReaderGenerator = formats.get_query_reader_generator( queryFileFormat )
        queryReader = \
            queryReaderGenerator( queryFileName, useQueries.topics.split() ) if useQueries.topics \
            else queryReaderGenerator( queryFileName )

        resultFileName = config.get_input_directory() + useQueries.result_file
        resultFileFormat = useQueries.result_file_format or config.get_default_result_file_format()
        resultReaderGenerator = formats.get_result_reader_generator( resultFileFormat )
        resultReader = resultReaderGenerator( resultFileName )

        qrPair = (queryReader,resultReader)
        qrPairs.append( qrPair )

    SessionReaderState.currentQRPairIndex = 0
    SessionReaderState.currentQRPairQueryIndex = 0

    def get_current_qr_pair():
        return qrPairs[ SessionReaderState.currentQRPairIndex ]

    def get_current_query_reader():
        (queryReader,resultReader) = get_current_qr_pair()
        return queryReader

    def skip_to_next_query():
        if SessionReaderState.currentQRPairQueryIndex == get_current_query_reader()[ 'get_length' ]() - 1:
            SessionReaderState.currentQRPairIndex += 1
            SessionReaderState.currentQRPairQueryIndex = 0
        else:
            SessionReaderState.currentQRPairQueryIndex += 1

        if SessionReaderState.currentQRPairIndex >= len(qrPairs):
            raise TriggerError("Session reader tried to advance to a non-existant query. " +
                "This is likely caused by improper triggering of 'nextQuery' in simulation description. " +
                "Please check if a next query is available before triggering the event.")

    def get_session_id():
        return session.id

    def get_current_query_text():
        (queryReader,resultReader) = get_current_qr_pair()
        (qid, queryText) = queryReader['get_query_by_index']( SessionReaderState.currentQRPairQueryIndex )
        return queryText

    def get_current_topic():
        (queryReader,resultReader) = get_current_qr_pair()
        (qid, queryText) = queryReader['get_query_by_index']( SessionReaderState.currentQRPairQueryIndex )
        return qid

    def get_current_relevance_level( docid ):
        return config.get_relevance_level( get_current_topic(), docid )

    def get_current_document_id( rank ):
        (queryReader,resultReader) = get_current_qr_pair()
        return resultReader[ 'get_document_id' ]( get_current_topic(), rank )

    def get_current_results_length():
        (queryReader,resultReader) = get_current_qr_pair()
        return resultReader[ 'get_results_length' ]( get_current_topic() )

    def get_amount_of_queries():
        amount = 0
        for (queryReader,resultReader) in qrPairs:
            amount += queryReader[ 'get_length' ]()
        return amount

    return {
            'skip_to_next_query': skip_to_next_query,
            'get_session_id': get_session_id,
            'get_current_query_text': get_current_query_text,
            'get_current_relevance_level': get_current_relevance_level,
            'get_current_document_id': get_current_document_id,
            'get_current_results_length': get_current_results_length,
            'get_amount_of_queries': get_amount_of_queries
            }

