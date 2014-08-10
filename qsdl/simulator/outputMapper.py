# -*- coding: latin-1 -*-
'''
Created on 17.10.2012

@author: Teemu Pääkkönen
'''
from qsdl.simulator import defaultOutputFormatter
from qsdl.simulator import csvOutputFormatter

def get_output_formatters():
    
    return {
            'default':  defaultOutputFormatter.get_output_formatter,
            'python': defaultOutputFormatter.get_output_formatter,
            'csv': csvOutputFormatter.get_output_formatter }
