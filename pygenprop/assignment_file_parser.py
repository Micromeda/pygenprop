#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: A parser for parsing genome properties longform files.
"""
import csv
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
    identifiers = []
    tsv_reader = csv.reader(interproscan_file, delimiter='\t')
    for row in tsv_reader:
        matched_interpro_member_database_id = row[4]
        identifiers.append(matched_interpro_member_database_id)

    return AssignmentCache(interpro_member_database_identifiers=identifiers,
                           sample_name=splitext(basename(interproscan_file.name))[0])
