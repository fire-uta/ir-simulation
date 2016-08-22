import sys
import csv
import ntpath


class DocStats:
  def __init__(self, file_path):
    self.file_path = file_path
    self.iterations = {}
    self.parse()

  def each_row(self):
    with open(self.file_path, 'r') as results_file:
      reader = csv.DictReader(results_file)
      for row in reader:
        yield row

  def file_name_without_extension(self):
    head, tail = ntpath.split(self.file_path)
    file_name = tail or ntpath.basename(head)
    root, ext = ntpath.splitext(file_name)
    return root

  def scanned_snippets_out_file_name(self):
    return self.file_name_without_extension() + '_scanned_snippets.csv'

  def viewed_documents_out_file_name(self):
    return self.file_name_without_extension() + '_viewed_documents.csv'

  def marked_relevant_out_file_name(self):
    return self.file_name_without_extension() + '_marked_relevant.csv'

  def queries_issued_out_file_name(self):
    return self.file_name_without_extension() + '_queries_issued.csv'

  def add_docid_to_iteration(self, docid, iterid, action):
    try:
      iteration = self.iterations[iterid]
    except KeyError:
      self.iterations[iterid] = {'seen_docs': [], 'viewed_docs': [], 'scanned_snippets': [], 'marked_relevant_docs': [], 'queries_issued': []}
      iteration = self.iterations[iterid]
    finally:
      iteration['seen_docs'].append(docid)
      iteration['seen_docs'] = list(set(iteration['seen_docs']))
      if action == 'view_document':
        iteration['viewed_docs'].append(docid)
        iteration['viewed_docs'] = list(set(iteration['viewed_docs']))
      if action == 'scan_snippet':
        iteration['scanned_snippets'].append(docid)
        iteration['scanned_snippets'] = list(set(iteration['scanned_snippets']))
      if action == 'mark_as_relevant':
        iteration['marked_relevant_docs'].append(docid)
        iteration['marked_relevant_docs'] = list(set(iteration['marked_relevant_docs']))
      if action == 'issue_query':
        iteration['queries_issued'].append(docid)
        iteration['queries_issued'] = list(set(iteration['queries_issued']))

  def parse(self):
    for row in self.each_row():
      if row['sessionId'] == 'rank':
        break
      self.add_docid_to_iteration(row['documentId'], row['iteration'], row['prevAction'])

  def open_csv_files_for_output(self):
    with open(self.scanned_snippets_out_file_name(), 'w') as scanned_snippets_file:
      with open(self.viewed_documents_out_file_name(), 'w') as viewed_documents_file:
        with open(self.marked_relevant_out_file_name(), 'w') as marked_relevant_file:
          with open(self.queries_issued_out_file_name(), 'w') as queries_issued_file:
            yield (scanned_snippets_file, viewed_documents_file, marked_relevant_file, queries_issued_file)

  def write_csv_files(self):
    for (scanned_snippets_file, viewed_documents_file, marked_relevant_file, queries_issued_file) in self.open_csv_files_for_output():
      scanned_snippets_writer = csv.DictWriter( scanned_snippets_file, fieldnames = ['iteration', 'docid'] )
      scanned_snippets_writer.writeheader()

      viewed_documents_writer = csv.DictWriter( viewed_documents_file, fieldnames = ['iteration', 'docid'] )
      viewed_documents_writer.writeheader()

      marked_relevant_writer = csv.DictWriter( marked_relevant_file, fieldnames = ['iteration', 'docid'] )
      marked_relevant_writer.writeheader()

      queries_issued_writer = csv.DictWriter( queries_issued_file, fieldnames = ['iteration', 'docid'] )
      queries_issued_writer.writeheader()

      for iteration_id, iteration in self.iterations.items():
        for scanned_snippet in iteration['scanned_snippets']:
          scanned_snippets_writer.writerow( { 'iteration': iteration_id, 'docid': scanned_snippet } )
        for viewed_document in iteration['viewed_docs']:
          viewed_documents_writer.writerow( { 'iteration': iteration_id, 'docid': viewed_document } )
        for marked_relevant in iteration['marked_relevant_docs']:
          marked_relevant_writer.writerow( { 'iteration': iteration_id, 'docid': marked_relevant } )
        for query_issued in iteration['queries_issued']:
          queries_issued_writer.writerow( { 'iteration': iteration_id, 'docid': query_issued } )


file_path = sys.argv[1]
doc_stats = DocStats( file_path )
doc_stats.write_csv_files()
