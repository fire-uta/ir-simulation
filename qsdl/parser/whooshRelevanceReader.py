# -*- coding: latin-1 -*-
'''
Created on 27.5.2015

@author: Teemu Pääkkönen
'''

import re
import ntpath
import csv
from qsdl.simulator.errors.ConfigurationInvalidError import ConfigurationInvalidError

class S: pass # Storage class
S.readers = {}

def get_relevance_reader( relevanceFile ):

    if S.readers.has_key( relevanceFile ):
        return S.readers[ relevanceFile ]

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

    def parse_relevance_file():
        file_info = _get_file_info( __get_bare_file_name( relevanceFile ) )
        rel_docs={}
        with open ( relevanceFile ) as fh:
            result_reader = csv.DictReader( fh, delimiter=',')
            for row in result_reader:
                try:
                    (topic_id, docid, rlevel) = (file_info['query_id'],row['docid'].strip(),row['trec_judgement'].strip())
                    document = topic_id,docid,rlevel
                    if not rel_docs.has_key(topic_id):
                        rel_docs[topic_id]={}
                    rel_docs[topic_id][docid] = document
                except KeyError as e:
                    raise ConfigurationInvalidError("Invalid data in relevance file %s: %s" % (relevanceFile, e))
        return rel_docs

    rels = parse_relevance_file()

    def get_relevance_level( topic, docid ):
        (q,d,rlevel) = rels[ topic ][ docid ]
        return rlevel

    def get_relevances():
        return rels

    def can_parse():
        with open( relevanceFile ) as ires:
            for line in ires:
                # Check only the first line
                return 'rank,docid,hover_occurrences,total_hover_time,doc_view_occurrences,total_doc_view_time,user_marked,trec_judgement,user_interaction' in line
        return False

    S.readers[ relevanceFile ] = {
            'get_relevance_level'   :   get_relevance_level,
            'get_relevances'        :   get_relevances,
            'can_parse'             :   can_parse
            }
    return S.readers[ relevanceFile ]

