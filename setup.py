# -*- coding: latin-1 -*-
from distutils.core import setup
setup(name='irsim',
      version='0.1.25',
      py_modules=['irsim', 'callbackLoader', 'stats', 'figures'],
      packages=['qsdl', 'qsdl.parser', 'qsdl.simulator', 'qsdl.simulator.errors', 'example-config'],
      package_data={'example-config': ['*.xml', '*.xsd']},
      data_files=[('', ['requirements.txt'])],
      scripts=['irsim'],
      url='http://www.github.com/fire-uta/ir-simulation/',
      author='Teemu Pääkkönen, University of Tampere',
      author_email='teemu.paakkonen@uta.fi'
      )
