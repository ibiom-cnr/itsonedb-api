#!/usr/bin/env python
"""
"""
from flask import Flask, jsonify, request, make_response
import sys, os
import json
from sqlalchemy import *

#import logging
#logging.basicConfig(filename='/tmp/readdb.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
#logging.info('start logging')

#______________________________________
def db_connection(db):
  """
  Connect to ItsOneDB.
  """

  engine = create_engine(db)
  engine.echo = False
  #print engine.table_names()
  connection = engine.connect()
  metadata = MetaData()

  return engine, connection, metadata

#______________________________________
def get_all_accessions(engine, connection, metadata):
  """
  Get all accession numbers from ITSOneDB
  """

  # Get sequence from Accession number
  gbentry_sequence = Table('gbentry_sequence', metadata, autoload=True, autoload_with=engine)
  select_gbentry_sequence = select([gbentry_sequence.c.gbentryAccession])
  result_gbentry_sequence = connection.execute(select_gbentry_sequence)

  all_accessions = []
  for row in result_gbentry_sequence:
    all_accessions.append(row[0])

  return jsonify(all_accessions)

#______________________________________
def get_sequences(engine, connection, metadata, accession_number):
  """
  function description
  put queries here
  """

  # Get sequence from Accession number
  gbentry_sequence = Table('gbentry_sequence', metadata, autoload=True, autoload_with=engine)
  select_gbentry_sequence = select([gbentry_sequence], and_(gbentry_sequence.c.gbentryAccession==accession_number))
  result_gbentry_sequence = connection.execute(select_gbentry_sequence)
  for row in result_gbentry_sequence: sequence_full = row[1]

  # Get ENA and HMM  localization
  its1feature = Table('its1feature', metadata, autoload=True, autoload_with=engine)
  select_its1feature = select([its1feature], and_(its1feature.c.GBentry_Accession==accession_number))
  result_its1feature = connection.execute(select_its1feature)
  for row in result_its1feature:
    hasGBannotation = row[1]
    GBstart = row[6]
    GBend = row[7]
    hasHMM = row[10]
    HMMstart = row[12]
    HMMend = row[13]

  try: hasGBannotation
  except NameError: hasGBannotation = None

  # ENA sequence output array
  ena_output = []
  ena_length = 0
  if hasGBannotation == 1:
    ena_sequence = sequence_full[GBstart-1:GBend]
    ena_length = GBend - GBstart + 1
    ena_output = [ena_sequence[i:i+80] for i in range(0, len(ena_sequence), 80)]

  try: hasHMM
  except NameError: hasHMM = None

  # HMM sequence output array
  hmm_output = []
  hmm_length = 0
  if hasHMM == 1:
    hmm_sequence = sequence_full[HMMstart-1:HMMend]
    hmm_length = HMMend - HMMstart + 1
    hmm_output = [hmm_sequence[i:i+80] for i in range(0, len(hmm_sequence), 80)]

  if hasGBannotation is None and hasHMM is None: return [None]*4

  return ena_output, ena_length, hmm_output, hmm_length

#______________________________________
def get_info(engine, connection, metadata, accession_number):
  """
  get info from tables
  put queries here
  """
  gbentry = Table('gbentry', metadata, autoload=True, autoload_with=engine)
  select_gbentry = select([gbentry], and_(gbentry.c.Accession==accession_number))
  result_gbentry = connection.execute(select_gbentry)
  for row in result_gbentry:
    version = row[1]
    description = row[3]
    length = row[4]
    taxon_db_xref = row[7]

  taxon_fungi = Table('taxon_fungi', metadata, autoload=True, autoload_with=engine)
  select_taxon_fungi = select([taxon_fungi], and_(taxon_fungi.c.db_xref==taxon_db_xref))
  result_taxon_fungi = connection.execute(select_taxon_fungi)
  for row in result_taxon_fungi:
    db_xref = row[0]
    taxon_name = row[1]
    lineage = row[2]
    taxontank_idtaxonrank = row[4]

  taxonrank = Table('taxonrank', metadata, autoload=True, autoload_with=engine)
  select_taxonrank = select([taxonrank], and_(taxonrank.c.idTaxonRank==taxontank_idtaxonrank))
  result_taxonrank = connection.execute(select_taxonrank)
  for row in result_taxonrank:
    taxon_rank_name =  row[1]

  return version, description, length, taxon_db_xref, taxon_name, lineage, taxon_rank_name

#______________________________________
def search_by_entry_accession(engine, connection, metadata, accession_number):
  
  ena_out, ena_len, hmm_out, hmm_len = get_sequences(engine, connection, metadata, accession_number)
  version, description, length, taxon_db_xref, taxon_name, lineage, taxon_rank_name = get_info(engine, connection, metadata, accession_number)

  if ena_out is None and hmm_out is None:
    return make_response(jsonify(message = "[ERROR] No matching neither accession nor GI"), 400)

  output = {
             'accession_number': accession_number,
             'version': version,
             'description': description,
             'sequence_length': length,
             'taxon_name': taxon_name,
             'taxon_rank': taxon_rank_name,
             'lineage': lineage
           }

  if ena_len > 0:
    ena_localization = '>%s_ITS1_ENA|ITS1 localized by ENA annotation, %s bp length;' % (accession_number, str(ena_len))
    output["ena_localization"] = ena_localization
    output["ena_sequences"] = ena_out

  if hmm_len > 0:
    hmm_output_prefix = '>%s_ITS1_HMM|ITS1 localized by HMM profiles, %s bp length;' % (accession_number, str(hmm_len))
    output["hmm_localization"] = hmm_localization
    output["hmm_sequences"] = hmm_out

  response = jsonify(output)

  response.status_code = 200

  return response

#______________________________________
def search_by_specie_name(engine, connection, metadata, specie_name):
  """
  #select * from gbentry where Description LIKE "%Aspergillus flavus%";
  """

  specie_name = specie_name.replace("&", " ")

  gbentry = Table('gbentry', metadata, autoload=True, autoload_with=engine)

  select_gbentry = select([gbentry], and_(gbentry.c.Description.like("%"+specie_name+"%")))
  result_gbentry = connection.execute(select_gbentry)
  accession_list = []
  for row in result_gbentry:
    accession_list.append(row[0])

  if not accession_list:
    return make_response(jsonify(message = "[ERROR] No matching species"), 400)

  output = {}

  for i in accession_list:
    # get sequences
    ena_out, ena_len, hmm_out, hmm_len = get_sequences(engine, connection, metadata, str(i))

    # get info
    version, description, length, taxon_db_xref, taxon_name, lineage, taxon_rank_name = get_info(engine, connection, metadata, str(i))

    if ena_out is None and hmm_out is None:
      return make_response(jsonify(message = "[ERROR] No matching neither accession nor GI"), 400)

    output[i] = {
                  'taxon_name': taxon_name,
                  'ENA': '0',
                  'HMM': '0',
                  'description': description,
                }

    if ena_len > 0:
      
      output[i]['ENA'] = '1'

    if hmm_len > 0:

      output[i]['HMM'] = '1'

  response = jsonify(output)

  response.status_code = 200

  return response

#______________________________________
def search_by_taxon_name(engine, connection, metadata, taxon_name):

  taxon_name = taxon_name.replace("&", " ")

  taxon_fungi = Table('taxon_fungi', metadata, autoload=True, autoload_with=engine)
  gbentry = Table('gbentry', metadata, autoload=True, autoload_with=engine)

  select_taxon_fungi = select([taxon_fungi], and_(taxon_fungi.c.Name.like("%"+taxon_name+"%")))
  result_taxon_fungi = connection.execute(select_taxon_fungi)
  accession_list = []
  for row in result_taxon_fungi:
    select_gbentry = select([gbentry], and_(gbentry.c.Taxon_db_xref==row[0]))
    result_gbentry = connection.execute(select_gbentry)
    print result_gbentry
    for row in result_gbentry:
      accession_list.append(row[0])

  if not accession_list:
    return make_response(jsonify(message = "[ERROR] No matching taxon"), 400)


  output = {}

  for i in accession_list:
    # get sequences
    ena_out, ena_len, hmm_out, hmm_len = get_sequences(engine, connection, metadata, str(i))

    # get info
    version, description, length, taxon_db_xref, taxon_name, lineage, taxon_rank_name = get_info(engine, connection, metadata, str(i))

    if ena_out is None and hmm_out is None:
      return make_response(jsonify(message = "[ERROR] No matching neither accession nor GI"), 400)

    output[i] = {
                  'taxon_name': taxon_name,
                  'ENA': '0',
                  'HMM': '0',
                  'description': description,
                }

    if ena_len > 0:

      output[i]['ENA'] = '1'

    if hmm_len > 0:

      output[i]['HMM'] = '1'


  response = jsonify(output)

  response.status_code = 200

  return response


#______________________________________
def itsonedb_read(action,name):

  itsonedb = 'mysql://galaxy:its1wbPASS@localhost:3306/itsonedb'
  engine, connection, metadata = db_connection(itsonedb)

  if action == "accession":
    if name == "all":
      return get_all_accessions(engine, connection, metadata)
    else:
      seqs = search_by_entry_accession(engine, connection, metadata, name)
      return seqs

  if action == "specie":
    accessions = search_by_specie_name(engine, connection, metadata, name)
    return accessions

  if action == "taxon":
    accessions = search_by_taxon_name(engine, connection, metadata, name)
    return accessions
