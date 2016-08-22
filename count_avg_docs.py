import csv
import sys
import difflib

class Stats:
  def __init__( self, sim_file ):
    self.sim_file = sim_file
    self.iterations = {}
    self.parse()

  def iteration( self, iterno ):
    try:
      return self.iterations[ str(iterno) ]
    except KeyError:
      self.iterations[ str(iterno) ] = { 'docs': [] }
      return self.iterations[ str(iterno) ]

  def parse( self ):
    for sim_doc in self.each_sim_row():
      self.iteration( sim_doc['iteration'] )[ 'docs' ].append( sim_doc['docid'] )

  def each_sim_row( self ):
    with open( self.sim_file, 'rb' ) as sim_file:
      reader = csv.DictReader( sim_file )
      for row in reader:
        yield row

  def stats( self ):
    stats = { 'all_number_docs': [] }
    for iterno, iteration in self.iterations.iteritems():
      stats['all_number_docs'].append( len( iteration['docs'] ) )

    stats[ 'avg_number_docs' ] = float( sum( stats['all_number_docs'] ) ) / float( len( stats['all_number_docs']))
    return stats


sim_file_path = sys.argv[1]
stats = Stats( sim_file_path )

print stats.stats()['avg_number_docs']
