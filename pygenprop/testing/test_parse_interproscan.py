#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2018)

Description: Parses InterProScan TSV files, assigns Genome Properties and writes them to JSON.
"""

import argparse

from pygenprop.assignment_file_parser import parse_interproscan_file
from pygenprop.database_file_parser import parse_genome_properties_flat_file
from pygenprop.results import GenomePropertiesResults

from pygenprop.lib import sanitize_cli_path


def main(args):
    """
    Creates a JSON file representing genome property assignments.
    :param args: The command line arguments.
    """

    genome_property_flat_file_path = sanitize_cli_path(args.input_genome_properties_flat_file)
    json_output_path = sanitize_cli_path(args.output_file_path)
    interproscan_file_path = (sanitize_cli_path(path) for path in args.input_interproscan_tsv_files)

    with open(genome_property_flat_file_path) as genome_property_file:
        genome_properties_tree = parse_genome_properties_flat_file(genome_property_file)

    interproscan_assignments = []
    for path in interproscan_file_path:
        with open(path) as interproscan_file:
            interproscan_assignments.append(parse_interproscan_file(interproscan_file))

    results = GenomePropertiesResults(*interproscan_assignments, genome_properties_tree=genome_properties_tree)

    with open(json_output_path, 'w') as json_file:
        results.to_json(json_file)


if __name__ == '__main__':
    cli_title = """Parses InterProScan TSV files, assigns Genome Properties and writes them to JSON."""

    parser = argparse.ArgumentParser(description=cli_title)
    parser.add_argument('-d', '--input_genome_properties_flat_file', metavar='DB', required=True,
                        help='The path to the genome properties flat file.')
    parser.add_argument('-o', '--output_file_path', metavar='OUT', required=True,
                        help='The path to the genome properties flat file.')
    parser.add_argument('-i', '--input_interproscan_tsv_files', metavar='ASSIGN', nargs='+',
                        required=True, help='The path to the genome properties flat file.')

    cli_args = parser.parse_args()

    main(cli_args)
