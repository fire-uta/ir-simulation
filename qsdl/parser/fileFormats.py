# -*- coding: latin-1 -*-
'''
Created on 19.10.2012

@author: Teemu Pääkkönen
'''

import qsdl.parser.lemurQueryReader as lemurQ
import qsdl.parser.trecResultsReader as trecRes
import qsdl.parser.trecRelevanceReader as trecRel
import qsdl.parser.trec2RelevanceReader as trec2Rel
import qsdl.parser.whooshQueryReader as whooshQ
import qsdl.parser.whooshResultsReader as whooshRes
import qsdl.parser.whooshRelevanceReader as whooshRel

def get_query_reader_generator( format_ ):
    return {
            'indri': lemurQ.get_query_reader,
            'whoosh': whooshQ.get_query_reader
            }[ format_ ]

def get_result_reader_generator( format_ ):
    return {
            'trec': trecRes.get_result_reader,
            'whoosh': whooshRes.get_result_reader
            }[ format_ ]

def get_relevance_reader_generator( format_ ):
    return {
            'trec': trecRel.get_relevance_reader,
            'trec2': trec2Rel.get_relevance_reader,
            'whoosh': whooshRel.get_relevance_reader
            }[ format_ ]

