# -*- coding: latin-1 -*-
'''
Created on 19.10.2012

@author: Teemu Pääkkönen
'''

import re
import qsdl.simulator.errors.UnknownDocumentError as UnknownDocumentError

class S: pass # Storage class
S.readers = {}

def get_result_reader( resultFile ):

    if S.readers.has_key( resultFile ):
        return S.readers[ resultFile ]
        
    def parse_result_file():
        result_set = {}
        with open( resultFile ) as ires:
            for line in ires:
                m = re.match('(\d+)\s+\S+\s+(\S+)\s+(\d+)\s+([-\d\.]+)',line)
                if m:
                    (qid, docid, rank, score) = (m.group(1), m.group(2), 
                                                     int(m.group(3)), m.group(4))
                    document = qid, docid, rank, score
                        
                    if not result_set.has_key(qid):
                        result_set[qid]={}
            
                    result_set[qid][rank] = document
        return result_set
    
    results = parse_result_file()
    
    def get_results_by_id( id_ ):
        return results[ id_ ]
    
    def get_document_id( topic, rank ):
        try:
            (qid, docid, rank_, score) = results[ topic ][ rank ]
            return docid
        except KeyError:
            raise UnknownDocumentError.UnknownDocumentError( 
                'No document id found for topic %s, rank %g' % (topic,rank) )
    
    def get_results_length( topic ):
        return len( results[ topic ] )
    
    S.readers[ resultFile ] = {
            'get_results_by_id': get_results_by_id,
            'get_document_id': get_document_id,
            'get_results_length': get_results_length
            }
    return S.readers[ resultFile ]
