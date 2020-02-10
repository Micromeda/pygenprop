#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2019)

Description: Provides various command line utilities for working with Micromeda files.
"""

import argparse
import os

import sqlalchemy
from pygenprop.assign import AssignmentCache, AssignmentCacheWithMatches
from pygenprop.assignment_database import Sample, PropertyAssignment, StepAssignment, InterProScanMatch, \
    Sequence
from pygenprop.assignment_file_parser import parse_interproscan_file, parse_interproscan_file_and_fasta_file
from pygenprop.database_file_parser import parse_genome_properties_flat_file
from pygenprop.lib import sanitize_cli_path
from pygenprop.results import GenomePropertiesResults, GenomePropertiesResultsWithMatches, \
    load_assignment_caches_from_database, load_assignment_caches_from_database_with_matches
from sqlalchemy import engine as SQLAlchemyEngine
from sqlalchemy.orm import sessionmaker


def main(args):
    """
    Collects input arguments and selects command to perform.
    :param args: The command line arguments.
    """

    if hasattr(args, 'output_file_path'):
        output_file_path = sanitize_cli_path(args.output_file_path)
    else:
        output_file_path = False

    if hasattr(args, 'build'):
        genome_properties_tree, sanitized_input_file_paths = get_shared_args(args)
        add_proteins = args.add_protein_sequences
        build_micromeda_file(genome_properties_tree, sanitized_input_file_paths, output_file_path, add_proteins)
    elif hasattr(args, 'merge'):
        genome_properties_tree, sanitized_input_file_paths = get_shared_args(args)
        merge_micromeda_files(genome_properties_tree, sanitized_input_file_paths, output_file_path)
    elif hasattr(args, 'info'):
        micromeda_file_info(args.input_file_path)
    else:
        parser.print_help()


def get_shared_args(args):
    """
    Extracts and prepares CLI arguments that are shared between build and merge commands.

    :param args: The command line arguments!
    :return: A genome properties tree and a list of sanitized input file paths.
    """
    genome_property_flat_file_path = sanitize_cli_path(args.input_genome_properties_flat_file)

    with open(genome_property_flat_file_path) as genome_property_file:
        genome_properties_tree = parse_genome_properties_flat_file(genome_property_file)

    sanitized_input_file_paths = [sanitize_cli_path(path) for path in args.input_file_paths]

    return genome_properties_tree, sanitized_input_file_paths


def build_micromeda_file(genome_properties_tree, interproscan_tsv_file_paths, output_file_path, add_proteins=False):
    """
    Takes a series of input InterProScan TSV files and uses their contents to build a Micromeda file.

    :param genome_properties_tree: A global genome properties tree object.
    :param interproscan_tsv_file_paths: One or more paths to InterProScan TSV files.
    :param output_file_path: The path and name of the output Micromeda file.
    :param add_proteins: Add protein from FASTA files with the same basenames and directory as the input IPR5 TSVs.'
    """
    assignments_caches = []
    for interproscan_path in interproscan_tsv_file_paths:
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

    if output_file_path:
        output_file_path = os.path.abspath(output_file_path)
    else:
        output_file_path = os.path.join(os.path.dirname(os.path.abspath(interproscan_tsv_file_paths[0])), 'data.micro')

    if add_proteins:
        results = GenomePropertiesResultsWithMatches(*assignments_caches, properties_tree=genome_properties_tree)
    else:
        results = GenomePropertiesResults(*assignments_caches, properties_tree=genome_properties_tree)

    engine = sqlalchemy.create_engine("sqlite:///" + output_file_path)
    results.to_assignment_database(engine)
    engine.dispose()


def merge_micromeda_files(genome_properties_tree, micromeda_file_paths, output_file_path):
    """
    Merges the results included in two or more Micromeda files and writes their contents to new Micromeda file.

    :param genome_properties_tree: A global genome properties tree object.
    :param micromeda_file_paths: The path to two or more Micromeda files.
    :param output_file_path: The path and name of the output Micromeda file.
    """
    if len(micromeda_file_paths) < 2:
        raise Exception('There must be at least two ')

    assignment_caches = []
    for micromeda_path in micromeda_file_paths:
        input_engine = sqlalchemy.create_engine("sqlite:///" + micromeda_path)
        matches = does_micromeda_file_have_matches(input_engine)

        if matches:
            current_assignment_caches = load_assignment_caches_from_database_with_matches(input_engine)
        else:
            current_assignment_caches = load_assignment_caches_from_database(input_engine)

        assignment_caches.extend(current_assignment_caches)

    if all(isinstance(cache, AssignmentCacheWithMatches) for cache in assignment_caches):
        results = GenomePropertiesResultsWithMatches(*assignment_caches, properties_tree=genome_properties_tree)
    elif all(isinstance(x, AssignmentCache) for x in assignment_caches):
        results = GenomePropertiesResults(*assignment_caches, properties_tree=genome_properties_tree)
    else:
        raise Exception('Input Micromeda files must all have protein sequences or must all not have protein sequences.')

    output_engine = sqlalchemy.create_engine("sqlite:///" + output_file_path)
    results.to_assignment_database(output_engine)
    output_engine.dispose()


def does_micromeda_file_have_matches(engine: SQLAlchemyEngine):
    """
    Checks if a Micromeda contains match information.

    :param engine: An SQLAlchemyEngine connection object of a Micromeda SQLite3 file.
    :return: True if the file contains matches.
    """
    session = sessionmaker(bind=engine)()
    # If the length of the sequence table is longer not equal 0 then there are protein
    # sequences stored in the Micromeda file an the contains match information.
    has_matches = session.query(Sequence).count() != 0
    return has_matches


def micromeda_file_info(micromeda_file_path):
    """
    List basic information about the contents of a Micromeda files.

    :param micromeda_file_path: The path to a micromeda file.
    """
    input_engine = sqlalchemy.create_engine("sqlite:///" + micromeda_file_path)
    session = sessionmaker(bind=input_engine)()

    sample_count = session.query(Sample).count()
    property_count = session.query(PropertyAssignment).count()
    step_count = session.query(StepAssignment).count()
    match_count = session.query(InterProScanMatch).count()
    sequence_count = session.query(Sequence).count()

    output = """
    The Micromeda file contains the following:
    
    Samples: {}
    Property Assignments: {}
    Step Assignments: {}
    InterProScan Matches: {}
    Protein Sequences: {}
    """.format(sample_count, property_count, step_count, match_count, sequence_count)

    print(output)


if __name__ == '__main__':
    cli_title = """A command line interface for generating and manipulating Micromeda pathway prediction files."""
    parser = argparse.ArgumentParser(description=cli_title)
    subparsers = parser.add_subparsers(help='Available Sub-commands')

    # =========================
    # Declare Build Sub-command
    build_help = """Generates Micromeda files containing genome properties pathway assignments 
    (optionally with protein sequence data)."""
    parser_build = subparsers.add_parser('build', help=build_help)

    parser_build.add_argument('-i', '--input_file_paths', metavar='TSV', nargs='+', required=True,
                              help='The paths to one or more InterProScan TSV files (space separated list).')
    parser_build.add_argument('-o', '--output_file_path', metavar='OUT',
                              help='The output path for including path and file name.')
    parser_build.add_argument('-d', '--input_genome_properties_flat_file', metavar='DB', required=True,
                              help='The path to the genome properties database flat file.')
    parser_build.add_argument('-p', '--add_protein_sequences', action='store_true',
                              help='Add protein sequences found in FASTA files with the same basenames'
                                   + ' and directory as the input IPR5 TSVs.')

    # Add attribute to tell main() what sub-command was called.
    parser_build.set_defaults(build=True)

    # =========================
    # Declare Merge Sub-command
    merge_help = """Merges one or more Micromeda files into a single output file."""
    parser_build = subparsers.add_parser('merge', help=merge_help)

    parser_build.add_argument('-i', '--input_file_paths', metavar='MICRO', nargs='+', required=True,
                              help='The paths to one or more Micromeda files (space separated list).')
    parser_build.add_argument('-o', '--output_file_path', metavar='OUT',
                              help='The output path for including path and file name.')
    parser_build.add_argument('-d', '--input_genome_properties_flat_file', metavar='DB', required=True,
                              help='The path to the genome properties database flat file.')
    parser_build.set_defaults(merge=True)

    # =========================
    # Declare Info Sub-command
    info_help = """Provides basic summary information about a Micromeda file."""
    parser_build = subparsers.add_parser('info', help=info_help)

    parser_build.add_argument('-i', '--input_file_path', metavar='MICRO', required=True,
                              help='The path to a Micromeda file.')
    parser_build.set_defaults(info=True)

    cli_args = parser.parse_args()
    main(cli_args)
