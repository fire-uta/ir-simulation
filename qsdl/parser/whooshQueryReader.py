# -*- coding: latin-1 -*-
'''
Created on 27.5.2015

@author: Teemu Pääkkönen
'''

import re
import ntpath

class S: pass # Storage class
S.readers = {}

def get_query_reader( queryFile, *ids ):

    if S.readers.has_key( queryFile ):
        if S.readers[ queryFile ].has_key( id(ids) ):
            return S.readers[ queryFile ][ id(ids) ]
    else:
        S.readers[ queryFile ] = {}


    queryOrder = []
    if ids:
        queryOrder = ids

    def __get_bare_file_name( file_name ):
        head, tail = ntpath.split( file_name )
        return tail or ntpath.basename( head )

    def _get_file_info( bare_file_name ):
        match = re.match( '([^-]+)-([^-]+)-([^-]+)_q([^.]+)', bare_file_name )
        if match is None: raise RuntimeError( "Unknown file encountered: %s" % (bare_file_name) )
        return {
            'query_id': match.group(4),
            'user_id': match.group(1),
            'condition': match.group(2),
            'topic_id': match.group(3)
        }

    def parse_query_file():
        file_info = _get_file_info( __get_bare_file_name( queryFile ) )
        queries = {}
        with open( queryFile ) as fh:
            for line in fh:
                if " QUERY_ISSUED " in line:
                    qid = file_info['query_id']
                    match = re.search( 'QUERY_ISSUED \d+ \'(.+)\'', line )
                    queryText = match.group(1)
                    queries[ qid ] = (qid, queryText)
                    if not ids:
                        queryOrder.append( qid )
        return queries

    queries = parse_query_file()

    def get_query_by_index( index ):
        return queries[ queryOrder[ index ] ]

    def get_query_by_id( id_ ):
        return queries[ id_ ]

    def get_length():
        return len(queries)

    S.readers[ queryFile ][ id(ids) ] = {
            'get_query_by_index': get_query_by_index,
            'get_query_by_id': get_query_by_id,
            'get_length': get_length
            }
    return S.readers[ queryFile ][ id(ids) ]


