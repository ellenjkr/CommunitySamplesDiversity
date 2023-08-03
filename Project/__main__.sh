cd input
input_folders=$(ls)
cd ..

export BLASTDB=/media/bioinfo/6tb_hdd/04_Blast_Databases/taxdb
for folder in $input_folders; do
	mkdir -p blast_output/$folder
	mkdir -p output/$folder
	for file in input/$folder/*.fa; do
		filename="${file/input\/$folder\//""}"
		filename="${filename/.fa/""}"
		
		echo $file
		time blastn \
		-db /media/bioinfo/6tb_hdd/04_Blast_Databases/BLAST_DB_nt/nt \
		-query $file \
		-outfmt "6 qseqid length score pident stitle sscinames" \
		-out blast_output/$folder/${filename}_blast.tsv \
		-num_threads 6 \
		-max_target_seqs 50
		
		python get_blast_statistics.py $folder ${filename}_blast.tsv
	done

done


