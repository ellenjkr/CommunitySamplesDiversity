import pandas as pd
import os
import pymysql.cursors
import concurrent.futures
import threading
from pathlib import Path


def get_organism_taxid(organism, cursor):
	cursor.execute(f"SELECT * FROM names WHERE name_txt = '{organism}' LIMIT 1")
	result = cursor.fetchone()
	if result is None:
		cursor.execute(f"SELECT * FROM names WHERE MATCH(name_txt) AGAINST('{organism}' IN NATURAL LANGUAGE MODE)")
		result = cursor.fetchone()

	taxid = result['tax_id']
	name_txt = result['name_txt']
 
	return taxid, name_txt


def get_taxonomy(especie):
	# Connect to the database
	connection = pymysql.connect(
		host='localhost',
		user='root',
		password='Amora#1000',
		database='ncbi_data',
		cursorclass=pymysql.cursors.DictCursor

	)
	taxonomies = {'Super-Reino': None, 'Filo': None, 'Classe': None, 'Ordem': None, 'Familia': None, 'Genero': None, 'Blast': None}
	#taxonomies = {'Blast': None, 'Genero': None, 'Familia': None, 'Ordem': None, 'Classe': None, 'Filo': None}
	with connection:
		with connection.cursor() as cursor:
			try:
				taxid, name_txt = get_organism_taxid(especie, cursor)
				
				cursor.execute(f"SELECT * FROM organisms WHERE tax_id = {taxid} LIMIT 1")
				# cursor.execute(f"SELECT * FROM organisms WHERE MATCH(tax_name) AGAINST('{especie}' IN NATURAL LANGUAGE MODE)")
				result = cursor.fetchone()

				taxonomies['Blast'] = especie
				taxonomies['Genero'] = result['genus']
				taxonomies['Familia'] = result['family']
				taxonomies['Ordem'] = result['_order']
				taxonomies['Classe'] = result['class']
				taxonomies['Filo'] = result['phylum']
				taxonomies['Super-Reino'] = result['superkingdom']
				
			except Exception as e:
				print(e)
				
				taxonomies['Blast'] = especie
				taxonomies['Genero'] = 'unclassified'
				taxonomies['Familia'] = 'unclassified'
				taxonomies['Ordem'] = 'unclassified'
				taxonomies['Classe'] = 'unclassified'
				taxonomies['Filo'] = 'unclassified'
				taxonomies['Super-Reino'] = 'unclassified'
				
		
	return taxonomies


def merge_results(path):
	for pos, file in enumerate(Path(path).glob('*.xlsx')):
		if pos == 1:
			file_name2 = file.stem
			file_name2 = file_name2.replace('blast_statistics_', '')
			df2 = pd.read_excel(file)
			merged_df = df.merge(df2, on='Blast', how='outer').fillna(0)
			merged_df.columns = ['Blast', file_name, file_name2]
			file_name = file_name2
		elif pos > 1:
			file_name2 = file.stem
			file_name2 = file_name2.replace('blast_statistics_', '')
			df2 = pd.read_excel(file, engine='openpyxl')
			merged_df = merged_df.merge(df2, on='Blast', how='outer').fillna(0)

			merged_df.columns = list(merged_df.columns)[:-1] + [file_name2]
			file_name = file_name2
		else:
			file_name = file.stem
			file_name = file_name.replace('blast_statistics_', '')
			df = pd.read_excel(file)

	return merged_df


def add_hierarchical_tax(merged_df, output_path):
	with concurrent.futures.ThreadPoolExecutor(max_workers=24) as executor:
		futures = [executor.submit(get_taxonomy, row['Blast']) for index, row in merged_df.iterrows()]
		results = [future.result() for future in futures]
		taxonomies_df = pd.json_normalize(results)

	output_df = taxonomies_df.merge(merged_df, on='Blast', how='outer').fillna('unclassified')
	output_df = output_df.rename(columns={'Blast': 'Especie'})


	output_df.replace('','unclassified', inplace=True)

	output_df.fillna('unclassified', inplace=True)

	output_df['Filo'][output_df.loc[output_df['Super-Reino'] == 'unclassified'].index] = 'unclassified'
	output_df['Classe'][output_df.loc[output_df['Filo'] == 'unclassified'].index] = 'unclassified'
	output_df['Ordem'][output_df.loc[output_df['Classe'] == 'unclassified'].index] = 'unclassified'
	output_df['Familia'][output_df.loc[output_df['Ordem'] == 'unclassified'].index] = 'unclassified'
	output_df['Genero'][output_df.loc[output_df['Familia'] == 'unclassified'].index] = 'unclassified'
	output_df['Especie'][output_df.loc[output_df['Genero'] == 'unclassified'].index] = 'unclassified'


	output_df.to_csv(f'{output_path}hierarchical_tax.tsv', sep='\t', index=False)


def run(config):
	merged_df = merge_results(config['OUTPUT_PATH'])
	add_hierarchical_tax(merged_df, config['OUTPUT_PATH'])


if __name__ == '__main__':
	run({'INPUT_PATH': 'input_test/', 'OUTPUT_PATH': 'output_test/'})