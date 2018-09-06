#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: Parses EBI genome properties assignment files.
"""

import argparse

from modules.genome_properties_longform_file_parser import parse_genome_property_longform_file

from modules.lib import sanitize_cli_path


def main(args):
    """
    Prints a human readable output of a genome properties assignment file.
    :param args: The command line arguments.
    """

    genome_property_assignment_file_path = sanitize_cli_path(args.input_genome_properties_file)

    with open(genome_property_assignment_file_path) as assignment_file:
        properties_assignment = parse_genome_property_longform_file(assignment_file)

    if properties_assignment is not None:
        print(properties_assignment)


if __name__ == '__main__':
    cli_title = """Parses a genome properties assignment file and prints its contents in a human readable format."""

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_genome_properties_file', metavar='DB', required=True,
                        help='The path to the genome properties flat file.')

    cli_args = parser.parse_args()

    main(cli_args)
