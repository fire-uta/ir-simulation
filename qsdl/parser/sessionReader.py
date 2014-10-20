# -*- coding: latin-1 -*-
'''
Created on 19.10.2012

@author: Teemu Pääkkönen
'''

import os
import re
import qsdl.parser.fileFormats as formats

class Struct:
    def __init__(self, **entries): self.__dict__.update(entries)

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

def read_sessions_from_directory( input_directory, sessions_directory ):
    session_map = {}

    directory = input_directory + sessions_directory
    for dirname, dirnames, filenames in os.walk( directory ):
        for filename in filenames:
            queryFileNameMatch = queryFilePattern.match( filename )
            if queryFileNameMatch is not None:
                handle_query_file_name_match( session_map, queryFileNameMatch, sessions_directory, input_directory )

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

    currentQRPairIndex = 0
    currentQRPairQueryIndex = 0

    def get_next_query():
        (queryReader,resultReader) = qrPairs[ currentQRPairIndex ]
        if currentQRPairQueryIndex == queryReader[ 'get_length' ]() - 1:
            currentQRPairIndex += 1
            currentQRPairQueryIndex = 0
            (queryReader,resultReader) = qrPairs[ currentQRPairIndex ]
        else:
            currentQRPairQueryIndex += 1
        return queryReader[ 'get_query_by_index' ]( currentQRPairQueryIndex )

    def get_session_id():
        return session.id

    def get_current_query_text():
        (queryReader,resultReader) = qrPairs[ currentQRPairIndex ]
        (qid, queryText) = queryReader['get_query_by_index']( currentQRPairQueryIndex )
        return queryText

    def get_current_topic():
        (queryReader,resultReader) = qrPairs[ currentQRPairIndex ]
        (qid, queryText) = queryReader['get_query_by_index']( currentQRPairQueryIndex )
        return qid

    def get_current_relevance_level( docid ):
        return config.get_relevance_level( get_current_topic(), docid )

    def get_current_document_id( rank ):
        (queryReader,resultReader) = qrPairs[ currentQRPairIndex ]
        return resultReader[ 'get_document_id' ]( get_current_topic(), rank )

    def get_current_results_length():
        (queryReader,resultReader) = qrPairs[ currentQRPairIndex ]
        return resultReader[ 'get_results_length' ]( get_current_topic() )

    def get_amount_of_queries():
        amount = 0
        for (queryReader,resultReader) in qrPairs:
            amount += queryReader[ 'get_length' ]()
        return amount

    return {
            'get_next_query': get_next_query,
            'get_session_id': get_session_id,
            'get_current_query_text': get_current_query_text,
            'get_current_relevance_level': get_current_relevance_level,
            'get_current_document_id': get_current_document_id,
            'get_current_results_length': get_current_results_length,
            'get_amount_of_queries': get_amount_of_queries
            }

