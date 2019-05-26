#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: A parser for parsing genome properties longform files.
"""
import csv
import skbio
import pandas as pd
from os.path import basename, splitext
from pygenprop.assign import AssignmentCache


def parse_genome_property_longform_file(longform_file):
    """
    Parses longform genome properties assignment files.

    :param longform_file: A longform genome properties assignment file handle object.
    :return: An assignment cache object.
    """
    property_id = ''
    step_number = ''

    assignment_cache = AssignmentCache(sample_name=splitext(basename(longform_file.name))[0])

    for line in longform_file:
        if 'PROPERTY:' in line:
            property_id = line.split(':')[1].strip()
        elif 'STEP NUMBER:' in line:
            step_number = int(line.split(':')[1].strip())
        elif 'RESULT:' in line:
            assignment = line.split(':')[1].strip().upper()

            if 'STEP' in line:
                assignment_cache.cache_step_assignment(property_id, step_number, assignment)
            else:
                assignment_cache.cache_property_assignment(property_id, assignment)
        else:
            continue

    return assignment_cache


def parse_interproscan_file(interproscan_file):
    """
    Parses InterProScan TSV files into an assignment cache.

    :param interproscan_file: A InterProScan file handle object.
    :return: An assignment cache object.
    """
    signatures_and_basic_match_info = create_match_dataframe(interproscan_file)
    identifiers = signatures_and_basic_match_info['Signature_Accession'].to_list()

    return AssignmentCache(interpro_signature_accessions=identifiers,
                           sample_name=splitext(basename(interproscan_file.name))[0])


def create_match_dataframe(interproscan_file):
    """
    Parses InterProScan TSV files

    :param interproscan_file: A InterProScan file handle object.
    :return: A pandas DataFrame with InterProScan information.
    """
    # Grab just columns 0, 4, 8 as these are the only ones we need.
    signatures_and_basic_match_info = pd.read_csv(interproscan_file, sep='\t', header=None).iloc[:, [0, 4, 8]]
    signatures_and_basic_match_info.columns = ['Protein_Accession', 'Signature_Accession', 'E-value']

    return signatures_and_basic_match_info


def create_sequence_dataframe(fasta_file):
    """
    Creates a DataFrame containing a series of protein sequences and their matches.

    :param fasta_file: A FASTA file handle object.
    :return: A pandas DataFrame with sequence information.
    """
    return pd.DataFrame(data=yield_identifier_sequence_mappings(fasta_file),
                        columns=['Protein_Accession', 'Sequence'])


def yield_identifier_sequence_mappings(fasta_file):
    """
    Yields identifier sequence pairings

    :param fasta_file: A FASTA file handle object.
    :return: A
    """
    for sequence in skbio.io.read(fasta_file, format='fasta'):
        yield (sequence.metadata['id'], str(sequence))
