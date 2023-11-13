import yaml
import subprocess
import get_blast_statistics
import generate_tax_file
from pathlib import Path
from Bio import SeqIO


def read_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


def concat_files(input_path):
    input_path = config['INPUT_PATH']

    all_sequences = []

    extensions = ['.fa', '.fasta', '.fas']
    fasta_files = [x for x in Path(input_path).iterdir() if x.suffix.lower() in extensions]
    for file in fasta_files:
        filename = file.stem
        record_dict = SeqIO.to_dict(SeqIO.parse(file, "fasta"))

        for seq in record_dict.values():
            seq.id = filename + '@@' + seq.id
            all_sequences.append(seq)

    with open(f"{input_path}all_sequences.fasta", "w") as output_handle:
        SeqIO.write(all_sequences, output_handle, "fasta")


if __name__ == "__main__":
    config = read_yaml("config.yaml")

    if config['OUTPUT_PATH'][-1] != '/':
        config['OUTPUT_PATH'] += '/'

    if config['INPUT_PATH'][-1] != '/':
        config['INPUT_PATH'] += '/'

    concat_files(config['INPUT_PATH'])

    subprocess.run(
        f"bash run_blast.sh -i {config['INPUT_PATH']}all_sequences.fasta -o {config['OUTPUT_PATH']} -d {config['DATABASE_PATH']} -t {config['TAX_DATABASE_PATH']}",
        shell=True,
        executable="/bin/bash",
    )

    get_blast_statistics.run(config)
    generate_tax_file.run(config)
    