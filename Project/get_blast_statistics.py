import pandas as pd
from Bio import SeqIO
from pathlib import Path


def get_df(output_path):
	df = pd.read_csv(f"{output_path}all_sequences_blast.tsv", sep='\t', names=['qseqid', 'length', 'score', 'pident', 'stitle', 'sscinames'])
	df[['sample_id', 'sequence_id']] = df['qseqid'].str.split('@@', n=1, expand=True)

	return df


def sep_df_by_sample(df):
	samples_dfs = {}
	grouped = df.groupby('sample_id')
	for group in grouped.groups:
		group_df = grouped.get_group(group)
		samples_dfs[group] = group_df

	return samples_dfs


def get_statistics(df):
	statistics_dict = {'Blast': []}

	sequences = df.sort_values(by='score', ascending=False).groupby('sequence_id')

	for sequence in sequences.groups.keys():
		sequence_results = sequences.get_group(sequence)
		blast_result = str(sequence_results['sscinames'].iloc[0])

		statistics_dict['Blast'].append(blast_result)

	statistics_df = pd.DataFrame(statistics_dict)
	blast_counts = statistics_df.value_counts(ascending=False).to_frame().reset_index()
	blast_counts.rename({0: 'Ocorrências'}, axis='columns', inplace=True)

	return blast_counts


def build_excel_file(statistics_df, output_file):
	writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
	statistics_df.to_excel(writer, sheet_name='Blast', startrow=1, header=False, index=False)
	worksheet = writer.sheets['Blast']
	(max_row, max_col) = statistics_df.shape
	column_settings = [{'header': column} for column in statistics_df.columns]
	worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings})
	worksheet.set_column(0, max_col - 1, 15)

	writer.close()


def run(config):
	output_path = config['OUTPUT_PATH']

	df = get_df(output_path)

	df.to_csv(f"{output_path}all_sequences.tsv", sep='\t', index=False)

	samples_dfs = sep_df_by_sample(df)

	for sample in samples_dfs.keys():
		statistics_df = get_statistics(samples_dfs[sample])
		build_excel_file(statistics_df, f'{output_path}blast_statistics_{sample}.xlsx')
		


if __name__ == '__main__':
	run({'INPUT_PATH': 'input_test/', 'OUTPUT_PATH': 'output_test/'})
