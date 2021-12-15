#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2019)

Description: A parser for parsing genome properties longform, InterProScan and FASTA files.
"""
from os.path import basename, splitext

import pandas as pd
import skbio

from pygenprop.assign import AssignmentCache, AssignmentCacheWithMatches


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
    identifiers = signatures_and_basic_match_info['Signature_Accession'].tolist()

    return AssignmentCache(interpro_signature_accessions=identifiers,
                           sample_name=splitext(basename(interproscan_file.name))[0])


def parse_interproscan_file_and_fasta_file(interproscan_file, fasta_file):
    """
    Parses InterProScan TSV files into an assignment cache with match information.

    :param interproscan_file: A InterProScan file handle object.
    :param fasta_file: An assignment cache with match information object.
    """
    signatures_and_basic_match_info = create_match_dataframe(interproscan_file)
    sequence_info = create_sequence_dataframe(fasta_file)

    return AssignmentCacheWithMatches(match_info_frame=signatures_and_basic_match_info,
                                      sequence_frame=sequence_info,
                                      sample_name=splitext(basename(interproscan_file.name))[0])


def create_match_dataframe(interproscan_file):
    """
    Parses InterProScan TSV files

    :param interproscan_file: A InterProScan file handle object.
    :return: A pandas DataFrame with InterProScan information.
    """
    # Grab just columns 0, 4, 8 as these are the only ones we need.
    return pd.read_csv(interproscan_file, sep='\t', header=None, usecols=[0, 4, 8], na_values="-",
                       names=['Protein_Accession', 'Signature_Accession', 'E-value'])


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
    Yields identifier sequence pairings from a FASTA file.

    :param fasta_file: A FASTA file handle object.
    :return: A
    """
    for sequence in skbio.io.read(fasta_file, format='fasta'):
        yield sequence.metadata['id'], str(sequence)
