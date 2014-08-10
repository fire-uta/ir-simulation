# -*- coding: latin-1 -*-
'''
Created on 19.10.2012

@author: Teemu Pääkkönen
'''

import re

class S: pass # Storage class
S.readers = {}

def get_relevance_reader( relevanceFile ):
    
    if S.readers.has_key( relevanceFile ):
        return S.readers[ relevanceFile ]
    
    def parse_relevance_file():
        rel_docs={}
        with open ( relevanceFile ) as fh:
            for line in fh:
                m=re.match(r'^(\d+)\s+\d+\s+(\S+)\s+(\S+)',line)
                if m:
                    (qid, docid, rlevel) = (m.group(1),m.group(2),m.group(3))
                    document = qid,docid,rlevel
                    if not rel_docs.has_key(qid):
                        rel_docs[qid]={}
                    rel_docs[qid][docid] = document
        return rel_docs
    
    rels = parse_relevance_file()
    
    def get_relevance_level( topic, docid ):
        (q,d,rlevel) = rels[ topic ][ docid ]
        return rlevel
    
    def get_relevances():
        return rels
    
    S.readers[ relevanceFile ] = {
            'get_relevance_level': get_relevance_level,
            'get_relevances': get_relevances
            }
    return S.readers[ relevanceFile ]
    