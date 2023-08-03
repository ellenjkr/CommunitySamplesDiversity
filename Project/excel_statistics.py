import pandas as pd
import glob
from pathlib import Path
import pymysql.cursors
import concurrent.futures


def get_organism_taxid(organism, cursor):
	cursor.execute(f"SELECT * FROM names WHERE name_txt = '{organism}' LIMIT 1")
	result = cursor.fetchone()
	if result is None:
		cursor.execute(f"SELECT * FROM names WHERE MATCH(name_txt) AGAINST('{organism}' IN NATURAL LANGUAGE MODE)")
		result = cursor.fetchone()

	taxid = result['tax_id']
	name_txt = result['name_txt']

	return taxid, name_txt


def get_taxonomy(especie, amostra):
	# Connect to the database
	connection = pymysql.connect(
		host='localhost',
		user='root',
		password='Amora#1000',
		database='ncbi_data',
		cursorclass=pymysql.cursors.DictCursor

	)
	taxonomies = {'Amostra': amostra, 'Gênero': None, 'Família': None, 'Ordem': None, 'Classe': None, 'Filo': None, 'Super-Reino': None}
	with connection:
		with connection.cursor() as cursor:
			try:
				taxid, name_txt = get_organism_taxid(especie, cursor)
				
				cursor.execute(f"SELECT * FROM organisms WHERE tax_id = {taxid} LIMIT 1")
				# cursor.execute(f"SELECT * FROM organisms WHERE MATCH(tax_name) AGAINST('{especie}' IN NATURAL LANGUAGE MODE)")
				result = cursor.fetchone()

				taxonomies['Gênero'] = result['genus']
				taxonomies['Família'] = result['family']
				taxonomies['Ordem'] = result['_order']
				taxonomies['Classe'] = result['class']
				taxonomies['Filo'] = result['phylum']
				taxonomies['Super-Reino'] = result['superkingdom']
				
			except Exception as e:				
				taxonomies['Gênero'] = 'unclassified'
				taxonomies['Família'] = 'unclassified'
				taxonomies['Ordem'] = 'unclassified'
				taxonomies['Classe'] = 'unclassified'
				taxonomies['Filo'] = 'unclassified'
				taxonomies['Super-Reino'] = 'unclassified'
				
		
	return taxonomies


def build_excel_sheet(writer, sheet_name, df):
	df.to_excel(writer, sheet_name=sheet_name, startrow=1, header=False, index=False)

	worksheet = writer.sheets[sheet_name]

	(max_row, max_col) = df.shape
	column_settings = [{'header': column} for column in df.columns]
	worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings})
	worksheet.set_column(0, max_col - 1, 15)

	return (writer, worksheet)


if __name__ == '__main__':
	

	input_path = 'input'

	all_samples = []
	for file in glob.glob(f"{input_path}/*.xlsx"):
		df = pd.read_excel(file)

		sample = Path(file).stem.replace('blast_statistics_', '')
		max_value = df.loc[df['Ocorrências'] == df['Ocorrências'].max()].reset_index(drop=True)
		if len(max_value) == 1:
			sample_statistics = pd.DataFrame(
				{
					'Amostra': [sample],
					'Reads': [df['Ocorrências'].sum()],
					'Maior Frequência': max_value['Ocorrências'],
					'%': [max_value['Ocorrências'][0] / df['Ocorrências'].sum() * 100],
					'Espécie': max_value['Blast']
				}
			)
			
		else:
			sample_statistics = pd.DataFrame(
				{
					'Amostra': [sample],
					'Reads': [df['Ocorrências'].sum()],
					'Maior Frequência': [max_value['Ocorrências'][0]],
					'%': [max_value['Ocorrências'][0] / df['Ocorrências'].sum() * 100],
					'Espécie': [max_value['Blast'][0]]
				}
			)
		all_samples.append(sample_statistics)



	samples_df = pd.concat(all_samples, axis=0).reset_index(drop=True)


	with concurrent.futures.ThreadPoolExecutor(max_workers=24) as executor:
		futures = [executor.submit(get_taxonomy, row['Espécie'], row['Amostra']) for index, row in samples_df.iterrows()]
		results = [future.result() for future in futures]
		taxonomies_df = pd.json_normalize(results)

	output_df = samples_df.merge(taxonomies_df, on='Amostra', how='outer').fillna('unclassified')

	writer = pd.ExcelWriter(f'lib3_animals_statistics.xlsx', engine='xlsxwriter')
	writer, worksheet = build_excel_sheet(writer, 'Estatísticas', output_df)
	writer.save()
