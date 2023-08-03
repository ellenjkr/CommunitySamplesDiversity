import pandas as pd
import os
import sys
from Bio import SeqIO


folder_name = sys.argv[1]
blast_file = sys.argv[2]
file_name = blast_file.replace('_blast.tsv', '')

blast_folder = f'blast_output/{folder_name}'
statistics_dict = {'Blast': []}

blast_df = pd.read_csv(f'{blast_folder}/{blast_file}', sep='\t', names=['sample', 'length', 'score', 'pident', 'stitle', 'sscinames'])
samples = blast_df.sort_values(by='score', ascending=False).groupby('sample')

fasta_file = blast_file.replace('_blast.tsv', '.fa')
record_dict = SeqIO.to_dict(SeqIO.parse(f"input/{folder_name}/{fasta_file}", "fasta"))

for sample in samples.groups.keys():
	sample_results = samples.get_group(sample)
	blast_result = str(sample_results['sscinames'].iloc[0])

	
	
	statistics_dict['Blast'].append(blast_result)

statistics_df = pd.DataFrame(statistics_dict)
blast_counts = statistics_df.value_counts(ascending=False).to_frame().reset_index()
blast_counts.rename({0: 'Ocorrências'}, axis='columns', inplace=True)

writer = pd.ExcelWriter(f'output/{folder_name}/blast_statistics_{file_name}.xlsx', engine='xlsxwriter')
blast_counts.to_excel(writer, sheet_name='Blast', startrow=1, header=False, index=False)
worksheet = writer.sheets['Blast']
(max_row, max_col) = blast_counts.shape
column_settings = [{'header': column} for column in blast_counts.columns]
worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings})
worksheet.set_column(0, max_col - 1, 15)

writer.close()