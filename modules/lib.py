#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: A set of helper functions.
"""

from modules.genome_property import parse_genome_property


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
    for marker, content in genome_property_record:
        if marker == previous_marker:
            trailing_marker_content.append(content)
        else:
            collapsed_marker_content = ' '.join(trailing_marker_content)
            new_collapsed_marker = (previous_marker, collapsed_marker_content)

            collapsed_genome_property_record.append(new_collapsed_marker)

            previous_marker = marker
            trailing_marker_content = [content]

    final_genome_property_record = collapse_step_evidence_and_gene_ontologys(collapsed_genome_property_record)
    return final_genome_property_record


def collapse_step_evidence_and_gene_ontologys(genome_property_record):
    """
    Pile up multiple consecutive 'EV' and 'TG' pairs to a single set of 'EV' and 'TG' pairs.
    Example:
        EV  C1
        TG  C2  ==== Goes To ====>> EV C1; C3;
        EV  C3                      TG C2; C4;
        EV  C4
    :param genome_property_record: A list of marker, content tuples representing genome property flat file lines.
    :return:    A list of reduced redundancy markers, content tuples representing genome property flat file lines.
                Inside steps, multiple 'EV' and 'TG' markers are piled up to two markers. See above for final layout.

    TODO:   There may be an issue with this and the sufficient key word. The sufficient key word may be only for one
            piece of evidence only.
    """
    current_evidence = []
    current_go_terms = []
    final_genome_property_record = []
    for marker, content in genome_property_record:
        if marker == '--':
            if current_evidence:
                final_genome_property_record.append(('EV', ' '.join(current_evidence)))
                current_evidence = []
            if current_go_terms:
                final_genome_property_record.append(('TG', ' '.join(current_go_terms)))
                current_go_terms = []
            final_genome_property_record.append(('--', ''))
        else:
            if marker == 'EV':
                current_evidence.append(content)
            elif marker == 'TG':
                current_go_terms.append(content)
            else:
                final_genome_property_record.append((marker, content))

    if current_evidence:
        final_genome_property_record.append(('EV', ' '.join(current_evidence)))
    if current_go_terms:
        final_genome_property_record.append(('TG', ' '.join(current_go_terms)))

    return final_genome_property_record


def parse_genome_property_file(genome_property_file):
    """
    A parses a genome property flat file.
    :param genome_property_file: A genome property file handle object.
    :return: A list of GenomeProperty objects.
    """
    genome_properties = []
    current_genome_property_record = []
    for line in genome_property_file:
        if not line.strip() == '//':
            current_genome_property_record.append(create_marker_and_content(line))
        else:
            collapsed_genome_property_record = collapse_genome_property_record(current_genome_property_record)
            new_genome_property = parse_genome_property(collapsed_genome_property_record)
            genome_properties.append(new_genome_property)
            current_genome_property_record = []

    return genome_properties
