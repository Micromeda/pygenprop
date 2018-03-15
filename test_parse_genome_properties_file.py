#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: Parses EBI genome properties flat files.
"""

from modules.lib import parse_genome_property_file, sanitize_cli_path
import argparse


def main(args):
    """
    Prints a human readable output of a genome properties flat file.
    :param args: The command line arguments.
    """

    genome_property_flat_file_path = sanitize_cli_path(args.input_genome_properties_file)

    with open(genome_property_flat_file_path) as genome_property_file:
        properties = parse_genome_property_file(genome_property_file)

    for genome_property in properties.values():
        parent_ids = [parent.id for parent in genome_property.parents]
        child_ids = [child.id for child in genome_property.children]

        if not parent_ids:
            parent_ids = "[ No Parent Genome Properties ]"

        if not child_ids:
            child_ids = "[ No Child Properties ]"

        print("\n" + genome_property.id + " (" + genome_property.name + ")" + " Type: [" + genome_property.type + "]" +
              " Parents: " + str(parent_ids) + " Children: " + str(child_ids))
        print(
            '=========================================================================================================')
        for step in genome_property.steps:
            print(str(step) + "\n")


if __name__ == '__main__':
    cli_title = """Parses a genome properties flat file and prints its contents in a human readable format."""

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_genome_properties_file', metavar='DB', required=True,
                        help='The path to the genome properties flat file.')

    cli_args = parser.parse_args()

    main(cli_args)
