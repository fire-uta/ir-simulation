# -*- coding: latin-1 -*-
from distutils.core import setup
setup(name='irsim',
      version='0.1.15',
      py_modules=['irsim', 'callbackLoader', 'stats', 'figures'],
      packages=['qsdl', 'qsdl.parser', 'qsdl.simulator', 'qsdl.simulator.errors'],
      data_files=[ ( 'example-config',
                     [
                      'example-config/config.xml',
                      'example-config/config-0.1.xsd',
                      'example-config/simulation.xml',
                      'example-config/qsdl-0.1.xsd',
                      'example-config/customConditionCallbacks.py',
                      'example-config/customCostCallbacks.py',
                      'example-config/customDecayCallbacks.py',
                      'example-config/customDerivedGainsCallbacks.py',
                      'example-config/customGainCallbacks.py',
                      'example-config/customTriggerCallbacks.py'
                      ] ),
                  ( '', ['irsim'] ) ],
      url='http://www.github.com/fire-uta/ir-simulation/',
      author='Teemu Pääkkönen, University of Tampere',
      author_email='teemu.paakkonen@uta.fi'
      )
