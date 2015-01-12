# -*- coding: latin-1 -*-
'''
Created on 19.10.2012

@author: Teemu Pääkkönen
'''

import xml.etree.ElementTree
import re

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

    def strip_indri_operators( queryText ):
        indriOpRegex = re.compile('#[^(]+\(([^)]+)\)')
        matchResult = indriOpRegex.match( queryText )
        if matchResult is None:
            return queryText
        return strip_indri_operators( matchResult.group(1) )

    def parse_query_file():
        queries = {}
        with open( queryFile ) as fh:
            queryFileTree = xml.etree.ElementTree.parse( fh )
            for query in queryFileTree.getroot().findall( 'query' ):
                qid = query.find( 'number' ).text
                queryText = query.find( 'text' ).text.strip()
                queryText = strip_indri_operators( queryText ).strip()
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


