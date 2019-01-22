#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: Parses EBI genome properties assignment files.
"""

import argparse

from pygenprop.assignment_parsers import parse_genome_property_longform_file
from pygenprop.flat_file_parser import parse_genome_property_file
from pygenprop.results import GenomePropertiesResults

from pygenprop.lib import sanitize_cli_path


def main(args):
    """
    Prints a human readable output of a genome properties assignment file.
    :param args: The command line arguments.
    """

    genome_property_flat_file_path = sanitize_cli_path(args.input_genome_properties_flat_file)
    json_output_path = sanitize_cli_path(args.output_file_path)
    assignment_file_paths = (sanitize_cli_path(path) for path in args.input_genome_properties_assignment_files)

    with open(genome_property_flat_file_path) as genome_property_file:
        genome_properties_tree = parse_genome_property_file(genome_property_file)

    assignments = []
    for path in assignment_file_paths:
        with open(path) as assignment_file:
            assignments.append(parse_genome_property_longform_file(assignment_file))

    results = GenomePropertiesResults(*assignments, genome_properties_tree=genome_properties_tree)

    with open(json_output_path, 'w') as json_file:
        results.to_json(json_file)


if __name__ == '__main__':
    cli_title = """Parses a genome properties assignment file and prints its contents in a human readable format."""

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--input_genome_properties_flat_file', metavar='DB', required=True,
                        help='The path to the genome properties flat file.')
    parser.add_argument('-o', '--output_file_path', metavar='OUT', required=True,
                        help='The path to the genome properties flat file.')
    parser.add_argument('-i', '--input_genome_properties_assignment_files', metavar='ASSIGN', nargs='+',
                        required=True, help='The path to the genome properties flat file.')

    cli_args = parser.parse_args()

    main(cli_args)
