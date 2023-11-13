while getopts i:o:d:t: flag
do
    case "${flag}" in
        i) input_file=${OPTARG};;
		o) output_path=${OPTARG};;
        d) database_path=${OPTARG};;
		t) tax_database_path=${OPTARG};;
    esac
done


export BLASTDB=${tax_database_path}
mkdir -p ${output_path}

basename "$input_file"
filename="$(basename -- $input_file)"

filename="${filename/.fasta/""}"

time blastn \
-db ${database_path} \
-query $input_file \
-outfmt "6 qseqid length score pident stitle sscinames" \
-out ${output_path}/${filename}_blast.tsv \
-num_threads 6 \
-max_target_seqs 50


