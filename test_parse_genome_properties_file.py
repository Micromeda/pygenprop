#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: Parses EBI genome properties flat files.
"""

import argparse

from modules.lib import sanitize_cli_path
from modules.flat_file_parser import parse_genome_property_file
import sys


def main(args):
    """
    Prints a human readable output of a genome properties flat file.
    :param args: The command line arguments.
    """

    genome_property_flat_file_path = sanitize_cli_path(args.input_genome_properties_file)

    with open(genome_property_flat_file_path) as genome_property_file:
        properties = parse_genome_property_file(genome_property_file)

    if properties is not None:
        print(str(len(properties)) + ' properties have been parsed.')
    else:
        print('Properties parsing has failed.')
        sys.exit(1)


if __name__ == '__main__':
    cli_title = """Parses a genome properties flat file and prints its contents in a human readable format."""

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_genome_properties_file', metavar='DB', required=True,
                        help='The path to the genome properties flat file.')

    cli_args = parser.parse_args()

    main(cli_args)
