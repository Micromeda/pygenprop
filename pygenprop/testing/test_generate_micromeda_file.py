#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2019)

Description: Creates a test Micromeda file.
"""

import argparse
import os
import sqlalchemy

from pygenprop.assignment_file_parser import parse_interproscan_file, parse_interproscan_file_and_fasta_file
from pygenprop.database_file_parser import parse_genome_properties_flat_file
from pygenprop.results import GenomePropertiesResults, GenomePropertiesResultsWithMatches

from pygenprop.lib import sanitize_cli_path


def main(args):
    """
    Prints a human readable output of a genome properties assignment file.
    :param args: The command line arguments.
    """

    genome_property_flat_file_path = sanitize_cli_path(args.input_genome_properties_flat_file)

    if args.output_file_path:
        micromeda_output_file = sanitize_cli_path(args.output_file_path)
    else:
        micromeda_output_file = False

    interproscan_tsv_files = [sanitize_cli_path(path) for path in args.interproscan_tsv_files]
    add_proteins = args.add_protein_sequences

    with open(genome_property_flat_file_path) as genome_property_file:
        genome_properties_tree = parse_genome_properties_flat_file(genome_property_file)

    assignments_caches = []
    for interproscan_path in interproscan_tsv_files:
        with open(interproscan_path) as tsv_file:
            # If the add protein sequences
            if add_proteins:
                path_with_no_extension = os.path.splitext(interproscan_path)[0]
                fasta_path = path_with_no_extension + '.faa'
                if not os.path.exists(fasta_path):
                    fasta_path = path_with_no_extension + '.fasta'

                with open(fasta_path) as fasta_file:
                    assignments_caches.append(parse_interproscan_file_and_fasta_file(tsv_file, fasta_file))
            else:
                assignments_caches.append(parse_interproscan_file(tsv_file))

    if micromeda_output_file:
        output_file_path = os.path.abspath(micromeda_output_file)
    else:
        output_file_path = os.path.join(os.path.dirname(os.path.abspath(interproscan_tsv_files[0])), 'data.micro')

    if add_proteins:
        results = GenomePropertiesResultsWithMatches(*assignments_caches, properties_tree=genome_properties_tree)
    else:
        results = GenomePropertiesResults(*assignments_caches, properties_tree=genome_properties_tree)

    sqlalchemy_url = "sqlite:///" + output_file_path
    engine = sqlalchemy.create_engine(sqlalchemy_url)
    results.to_assignment_database(engine)
    engine.dispose()


if __name__ == '__main__':
    cli_title = """Generates Micromeda files (SQLite3) containing genome properties pathway assignments 
    (optionally with protein sequence data)."""

    parser = argparse.ArgumentParser(description=cli_title)
    parser.add_argument('-d', '--input_genome_properties_flat_file', metavar='DB', required=True,
                        help='The path to the genome properties database flat file.')
    parser.add_argument('-o', '--output_file_path', metavar='OUT',
                        help='The output path for including path and file name.')
    parser.add_argument('-i', '--interproscan_tsv_files', metavar='TSV', nargs='+',
                        required=True, help='The paths to one or more InterProScan TSV files (space separated list).')
    parser.add_argument('-p', '--add_protein_sequences', action='store_true',
                        help='Add protein sequences found in FASTA files with the same basenames'
                             + ' and directory as the input IPR5s TSVs.')

    cli_args = parser.parse_args()

    main(cli_args)
