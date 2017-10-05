#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: A set of helper functions.
"""

from modules.database_reference import DatabaseReference
from modules.genome_property import GenomeProperty
from modules.literature_reference import LiteratureReference
from modules.step import Step


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

    return final_genome_property_record


def parse_genome_property(genome_property_record):
    """
    Parses a single genome property from a genome property record.
    :param genome_property_record:  A list of marker, content tuples representing genome property flat file lines.
    :return: A single genome property object.
    """
    # A list of record markers related to the genome property.
    core_genome_property_markers = ['AC', 'DE', 'TP', 'TH', 'PN', 'CC', '**']
    gathered_core_genome_property_markers = {}

    has_references = False
    has_databases = False
    has_steps = False

    for marker, content in genome_property_record:
        if marker == 'RN':
            has_references = True
        elif marker == 'DC':
            has_databases = True
        elif marker == 'SN':
            has_steps = True
        elif marker in core_genome_property_markers:
            if marker == 'TH':
                content = int(content)
            gathered_core_genome_property_markers[marker] = content

    if has_references:
        references = parse_literature_references(genome_property_record)
    else:
        references = []

    if has_databases:
        databases = parse_database_references(genome_property_record)
    else:
        databases = []

    if has_steps:
        steps = parse_steps(genome_property_record)
    else:
        steps = []

    new_genome_property = GenomeProperty(accession_id=gathered_core_genome_property_markers.get('AC'),
                                         name=gathered_core_genome_property_markers.get('DE'),
                                         property_type=gathered_core_genome_property_markers.get('TP'),
                                         threshold=gathered_core_genome_property_markers.get('TH'),
                                         parent=gathered_core_genome_property_markers.get('PN'),
                                         description=gathered_core_genome_property_markers.get('CC'),
                                         private_notes=gathered_core_genome_property_markers.get('**'),
                                         references=references,
                                         databases=databases,
                                         steps=steps)
    return new_genome_property


def parse_literature_references(genome_property_record):
    """
    Parses literature references from a genome properties record.
    :param genome_property_record: A list of marker, content tuples representing genome property flat file lines.
    :return: A list of LiteratureReference objects.
    """
    # A list of record markers related to literature references.
    literature_reference_markers = ['RN', 'RM', 'RT', 'RA', 'RL']

    literature_references = []
    current_literature_reference = {}
    for marker, content in genome_property_record:
        if marker in literature_reference_markers:
            if marker in current_literature_reference:
                literature_references.append(LiteratureReference(number=current_literature_reference.get('RN'),
                                                                 pubmed_id=current_literature_reference.get('RM'),
                                                                 title=current_literature_reference.get('RT'),
                                                                 authors=current_literature_reference.get('RA'),
                                                                 citation=current_literature_reference.get('RL')))
                if marker == 'RN':
                    content = int(content.strip('[]'))

                current_literature_reference = {marker: content}
            else:
                if marker == 'RN':
                    content = int(content.strip('[]'))

                current_literature_reference[marker] = content

    literature_references.append(LiteratureReference(number=current_literature_reference.get('RN'),
                                                     pubmed_id=current_literature_reference.get('RM'),
                                                     title=current_literature_reference.get('RT'),
                                                     authors=current_literature_reference.get('RA'),
                                                     citation=current_literature_reference.get('RL')))
    return literature_references


def parse_steps(genome_property_record):
    """
    Parses steps from a genome properties record.
    :param genome_property_record: A list of marker, content tuples representing genome property flat file lines.
    :return: A list of Step objects.
    """
    step_markers = ['SN', 'ID', 'DN', 'RQ', 'EV', 'TG']
    steps = []
    try:
        current_step = {}
        for marker, content in genome_property_record:
            if marker in step_markers:
                if marker in current_step:
                    steps.append(Step(number=current_step.get('SN'), identifier=current_step.get('ID'),
                                      name=current_step.get('DN'), evidence=current_step.get('EV'),
                                      gene_ontology_id=current_step.get('TG'), required=current_step.get('RQ'),
                                      sufficient=current_step.get('SF')))

                    if marker == 'SN':
                        content = int(content)

                    current_step = {marker: content}
                else:
                    if marker == 'SN':
                        content = int(content)
                    elif marker == 'EV':
                        split_content = filter(None, content.split(';'))
                        cleaned_content = list(map(lambda evidence: evidence.strip(), split_content))
                        if 'sufficient' in cleaned_content:
                            current_step['SF'] = True
                        else:
                            current_step['SF'] = False
                        content = [evidence for evidence in cleaned_content if evidence != 'sufficient']
                    elif marker == 'RQ':
                        if int(content) == 1:
                            content = True
                        else:
                            content = False

                    current_step[marker] = content

        steps.append(Step(number=current_step.get('SN'), identifier=current_step.get('ID'),
                          name=current_step.get('DN'), evidence=current_step.get('EV'),
                          gene_ontology_id=current_step.get('TG'), required=current_step.get('RQ'),
                          sufficient=current_step.get('SF')))
    except TypeError:
        print('yolo')
    finally:
        return steps


def parse_database_references(genome_property_record):
    """
    Parses database reference from a genome properties record.
    :param genome_property_record: A list of marker, content tuples representing genome property flat file lines.
    :return: A list of DatabaseReference objects.
    """
    database_reference_markers = ['DC', 'DR']

    database_references = []
    current_database_reference = {}
    for marker, content in genome_property_record:
        if marker in database_reference_markers:
            if marker in current_database_reference:
                database_references.append(DatabaseReference(record_title=current_database_reference.get('DC'),
                                                             database_name=current_database_reference.get('DN'),
                                                             record_ids=current_database_reference.get('DI')))

                current_database_reference = {marker: content}
            else:
                if marker == 'DR':
                    split_content = filter(None, content.split(';'))
                    cleaned_content = list(map(lambda evidence: evidence.strip(), split_content))
                    database_name = cleaned_content[0]
                    database_records = cleaned_content[1:]
                    current_database_reference['DN'] = database_name
                    current_database_reference['DI'] = database_records

                current_database_reference[marker] = content

    database_references.append(DatabaseReference(record_title=current_database_reference.get('DC'),
                                                 database_name=current_database_reference.get('DN'),
                                                 record_ids=current_database_reference.get('DI')))
    return database_references


def parse_genome_property_file(genome_property_flat_file_path):
    """
    A parses a genome property flat file.
    :param genome_property_flat_file_path: The path to the genome property flat file.
    :return: A list of GenomeProperty objects.
    """
    genome_properties = []
    current_genome_property_record = []
    with open(genome_property_flat_file_path) as gen_prop_file:
        for line in gen_prop_file:
            if not line.strip() == '//':
                current_genome_property_record.append(create_marker_and_content(line))
            else:
                collapsed_genome_property_record = collapse_genome_property_record(current_genome_property_record)
                new_genome_property = parse_genome_property(collapsed_genome_property_record)
                genome_properties.append(new_genome_property)
                current_genome_property_record = []

    return genome_properties
