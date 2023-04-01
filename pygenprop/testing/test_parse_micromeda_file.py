#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: Parses EBI genome properties flat files.
"""

import argparse
import logging

import sqlalchemy
from pygenprop.lib import sanitize_cli_path
from pygenprop.database_file_parser import parse_genome_properties_flat_file
import sys

from pygenprop.results import load_assignment_caches_from_database_with_matches, GenomePropertiesResultsWithMatches

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

def main(args):
    """
    Prints a human-readable output of a genome properties flat file.
    :param args: The command line arguments.
    """

    genome_property_flat_file_path = sanitize_cli_path(args.input_genome_properties_file)
    micromeda_file_path = sanitize_cli_path(args.input_micromeda_file)

    with open(genome_property_flat_file_path) as genome_property_file:
        logging.info('Opening the genome properites file')
        properties = parse_genome_properties_flat_file(genome_property_file)
        logging.info('Opening the micromeda file')
        input_engine = sqlalchemy.create_engine("sqlite:///" + micromeda_file_path)
        logging.info('Creating Assignment Caches')
        current_assignment_caches = load_assignment_caches_from_database_with_matches(input_engine)
        logging.info('Creating Results Caches')
        results = GenomePropertiesResultsWithMatches(*current_assignment_caches, properties_tree=properties)

    sys.exit(1)


if __name__ == '__main__':
    cli_title = """Parses a genome properties database flat file and counts the number of properties parsed."""

    parser = argparse.ArgumentParser(description=cli_title)
    parser.add_argument('-i', '--input_micromeda_file', metavar='MICRO', required=True,
                        help='The path to the micromeda file.')
    parser.add_argument('-d', '--input_genome_properties_file', metavar='DB', required=True,
                        help='The path to the genome properties flat file.')

    cli_args = parser.parse_args()

    main(cli_args)
