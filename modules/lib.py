#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: A set of helper functions.
"""

from modules.genome_property import parse_genome_property
from modules.genome_property import build_genome_property_connections
from os import path


def create_marker_and_content(genome_property_flat_file_line):
    """
    Splits a list of lines from a genome property file into marker, content pairs.
    :param genome_property_flat_file_line: A line from a genome property flat file line.
    :return: A tuple containing a marker, content pair.
    """
    columns = genome_property_flat_file_line.split('  ')
    marker = columns[0].strip()
    content = ''.join(columns[1:]).rstrip()
    return marker, content


def collapse_genome_property_record(genome_property_record):
    """
    The standard genome property record wraps every 80 lines. This function unwraps the record.
    :param genome_property_record: A list of marker, content tuples representing genome property flat file lines.
    :return:    A list of reduced redundancy markers, content tuples representing genome property flat file lines.
                Consecutive markers (often 'CC' and '**') markers are collapsed to one tuple.
                Inside steps, multiple 'EV' and 'TG' markers are piled up to two markers.
    """
    collapsed_genome_property_record = []

    trailing_marker_content = []
    previous_marker = genome_property_record[0][0]
    no_collapse_makers = ['EV']
    for marker, content in genome_property_record:
        if marker in no_collapse_makers:
            collapsed_genome_property_record.append((marker, content))
        elif marker == previous_marker:
            trailing_marker_content.append(content)
        else:
            collapsed_marker_content = ' '.join(trailing_marker_content)
            new_collapsed_marker = (previous_marker, collapsed_marker_content)

            collapsed_genome_property_record.append(new_collapsed_marker)

            previous_marker = marker
            trailing_marker_content = [content]

    return collapsed_genome_property_record


def parse_genome_property_file(genome_property_file):
    """
    A parses a genome property flat file.
    :param genome_property_file: A genome property file handle object.
    :return: A dictionary of GenomeProperty objects.
    """
    genome_properties = {}
    current_genome_property_record = []
    for line in genome_property_file:
        if not line.strip() == '//':
            current_genome_property_record.append(create_marker_and_content(line))
        else:
            collapsed_genome_property_record = collapse_genome_property_record(current_genome_property_record)
            new_genome_property = parse_genome_property(collapsed_genome_property_record)
            genome_properties[new_genome_property.id] = new_genome_property
            current_genome_property_record = []

    # Build parent-child connections between genome properties in the dict.
    build_genome_property_connections(genome_properties)

    return genome_properties


def print_genome_properties(properties):
    """
    Prints a human readable summery for all properties in a genome properties dictionary.
    :param properties: A dictionary containing multiple genome properties objects.
    """
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


def sanitize_cli_path(cli_path):
    """
    Performs expansion of '~' and shell variables such as "$HOME" into absolute paths.
    :param cli_path: The path to expand
    :return: An expanded path.
    """
    sanitized_path = path.expanduser(path.expandvars(cli_path))
    return sanitized_path
