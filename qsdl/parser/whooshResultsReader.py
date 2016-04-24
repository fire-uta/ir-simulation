# -*- coding: latin-1 -*-
'''
Created on 26.5.2015

@author: Teemu Pääkkönen
'''

import re
import ntpath
import csv
import qsdl.simulator.errors.UnknownDocumentError as UnknownDocumentError
from qsdl.simulator.errors.ConfigurationInvalidError import ConfigurationInvalidError

class S: pass # Storage class
S.readers = {}

def get_result_reader( resultFile ):

    if S.readers.has_key( resultFile ):
        return S.readers[ resultFile ]

    def __get_bare_file_name( file_name ):
        head, tail = ntpath.split( file_name )
        return tail or ntpath.basename( head )

    def _get_file_info( bare_file_name ):
        match = re.match( '([^-]+)-([^-]+)-([^-]+)_q([^r]+)r', bare_file_name )
        if match is None: raise RuntimeError( "Unknown file encountered: %s" % (bare_file_name) )
        return {
            'query_id': match.group(4),
            'user_id': match.group(1),
            'condition': match.group(2),
            'topic_id': match.group(3)
        }

    def __parse():
        file_info = _get_file_info( __get_bare_file_name( resultFile ) )
        result_set = {}
        with open( resultFile ) as result_file:
          result_reader = csv.DictReader( result_file, delimiter=',')
          for row in result_reader:
              qid = file_info['query_id']
              rank = row['rank'].strip()
              document = (qid, row['docid'].strip(), rank)
              if not result_set.has_key(qid):
                  result_set[str(qid)]={}
              result_set[qid][int(rank)] = document
        return result_set

    results = __parse()

    def get_results_by_id( id_ ):
        return results[ id_ ]

    def get_document_id( topic, rank ):
        try:
            (qid, docid, rank_) = results[ str(topic) ][ int(rank) ]
            return docid
        except KeyError:
            raise UnknownDocumentError.UnknownDocumentError(
                'No document id found for query id / topic %s, rank %g, in %s' % (topic,rank,resultFile) )

    def get_results_length( topic ):
        try:
            return len( results[ topic ] )
        except KeyError:
            raise ConfigurationInvalidError( 'Failed to get results length for topic \'%s\'. Results are available for topics: %s.' % ( topic, results.keys() ) )


    def can_parse():
        with open( resultFile ) as ires:
            for line in ires:
                # Check only the first line
                return 'rank,docid,hover_occurrences,total_hover_time,doc_view_occurrences,total_doc_view_time,user_marked,trec_judgement,user_interaction' in line
        return False


    S.readers[ resultFile ] = {
            'get_results_by_id'     :   get_results_by_id,
            'get_document_id'       :   get_document_id,
            'get_results_length'    :   get_results_length,
            'can_parse'             :   can_parse,
            'file_name'             :   resultFile
            }
    return S.readers[ resultFile ]
