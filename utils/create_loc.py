#!/usr/bin/env python

import ast

with open("accessions_r138.list") as fin:
  ini_list = fin.read().replace('\n', '')

accessions_list = ast.literal_eval(ini_list) 
print(type(accessions_list))

fout = open('accessions_r138.txt', 'w')
for accession in accessions_list:
  #print(accession)
  fout.write(accession + "\n")
