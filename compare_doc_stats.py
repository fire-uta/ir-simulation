import csv
import sys
import difflib

class Comparison:
  def __init__( self, sim_file, real_file ):
    self.sim_file = sim_file
    self.real_file = real_file
    self.iterations = {}
    self.real_session = { 'docs': [] }
    self.parse()

  def iteration( self, iterno ):
    try:
      return self.iterations[ str(iterno) ]
    except KeyError:
      self.iterations[ str(iterno) ] = { 'docs': [] }
      return self.iterations[ str(iterno) ]

  def parse( self ):
    for doc in self.each_real_row():
      self.real_session['docs'].append( doc['docid'] )
    for sim_doc in self.each_sim_row():
      self.iteration( sim_doc['iteration'] )[ 'docs' ].append( sim_doc['docid'] )

  def each_sim_row( self ):
    with open( self.sim_file, 'rb' ) as sim_file:
      reader = csv.DictReader( sim_file )
      for row in reader:
        yield row

  def each_real_row( self ):
    with open( self.real_file, 'rb' ) as real_file:
      reader = csv.DictReader( real_file )
      for row in reader:
        yield row

  def stats( self ):
    stats = { 'all_ratios': [], 'all_similarities': [] }
    for iterno, iteration in self.iterations.iteritems():
      intersection = list( set( iteration[ 'docs' ] ) & set( self.real_session[ 'docs' ] ) )
      ratio = (float(len(intersection)) / float(len(self.real_session['docs'])))
      stats['all_ratios'].append( ratio )

      matcher = difflib.SequenceMatcher( None, iteration['docs'], self.real_session['docs'] )
      stats['all_similarities'].append( matcher.ratio() )
    stats[ 'avg_ratio' ] = float( sum( stats['all_ratios'] ) ) / float( len( stats['all_ratios']))
    stats[ 'avg_similarity' ] = float( sum( stats['all_similarities'] ) ) / float( len( stats['all_similarities']))
    return stats


sim_file_path = sys.argv[1]
real_file_path = sys.argv[2]
comparison = Comparison( sim_file_path, real_file_path )

print comparison.stats()['avg_ratio']
