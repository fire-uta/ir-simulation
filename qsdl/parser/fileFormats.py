# -*- coding: latin-1 -*-
'''
Created on 19.10.2012

@author: Teemu Pääkkönen
'''

import qsdl.parser.lemurQueryReader as lemurQ
import qsdl.parser.trecResultsReader as trecRes
import qsdl.parser.trecRelevanceReader as trecRel
import qsdl.parser.trec2RelevanceReader as trec2Rel

def get_query_reader_generator( format_ ):
    return {
            'indri': lemurQ.get_query_reader
            }[ format_ ]
            
def get_result_reader_generator( format_ ):
    return {
            'trec': trecRes.get_result_reader
            }[ format_ ]
            
def get_relevance_reader_generator( format_ ):
    return {
            'trec': trecRel.get_relevance_reader,
            'trec2': trec2Rel.get_relevance_reader
            }[ format_ ]
            
