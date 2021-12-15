#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: A parser for parsing genome properties flat files into a rooted DAG of genome properties.
"""

from pygenprop.step import Step
from pygenprop.evidence import Evidence
from pygenprop.genome_property import GenomeProperty
from pygenprop.functional_element import FunctionalElement
from pygenprop.database_reference import DatabaseReference
from pygenprop.tree import GenomePropertiesTree
from pygenprop.literature_reference import LiteratureReference
from itertools import groupby


def parse_genome_properties_flat_file(genome_property_file):
    """
    A parses a genome property flat file.

    :param genome_property_file: A genome property file handle object.
    :return: A GenomePropertyTree object.
    """
    genome_properties = []
    current_genome_property_record = []
    for line in genome_property_file:
        if not line.strip() == '//':
            current_genome_property_record.append(create_marker_and_content(line))
        else:
            collapsed_genome_property_record = unwrap_genome_property_record(current_genome_property_record)
            new_genome_property = parse_genome_property(collapsed_genome_property_record)
            genome_properties.append(new_genome_property)
            current_genome_property_record = []

    genome_properties_tree = GenomePropertiesTree(*genome_properties)

    return genome_properties_tree


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


def unwrap_genome_property_record(genome_property_record):
    """
    The standard genome property record wraps every 80 lines. This function unwraps the record.

    :param genome_property_record: A list of marker, content tuples representing genome property flat file lines.
    :return:    A list of reduced redundancy markers, content tuples representing genome property flat file lines.
                Consecutive markers (often 'CC' and '**') markers are collapsed to one tuple.
    """
    collapsed_genome_property_record = []
    non_collapse_makers = ('EV', 'RQ')

    # Bin rows with consecutive markers using groupby. Collapse consecutive markers in bin.
    for bin_marker, binned in groupby(genome_property_record, lambda x: x[0]):
        bin_contents = (row_content for row_marker, row_content in binned)

        if bin_marker in non_collapse_makers:
            for content in bin_contents:
                collapsed_genome_property_record.append((bin_marker, content))
        else:
            collapsed_genome_property_record.append((bin_marker, ' '.join(bin_contents)))

    return collapsed_genome_property_record


def parse_genome_property(genome_property_record):
    """
    Parses a single genome property from a genome property record.

    :param genome_property_record:  A list of marker, content tuples representing genome property flat file lines.
    :return: A single genome property object.
    """
    # A list of record markers related to the genome property.
    core_genome_property_markers = ('AC', 'DE', 'TP', 'TH', 'PN', 'CC', '**')
    gathered_core_genome_property_markers = {}

    reference_index = False
    database_index = False
    step_index = False

    current_index = 0
    for marker, content in genome_property_record:
        if marker == 'RN':
            if not reference_index:
                reference_index = current_index
        elif marker == 'DC':
            if not database_index:
                database_index = current_index
        elif marker == '--':
            step_index = current_index + 1
            break  # If we have reach steps we have covered all core_genome_property_markers and can leave the loop.
        elif marker in core_genome_property_markers:
            if marker == 'TH':
                content = int(content)
            gathered_core_genome_property_markers[marker] = content

        current_index = current_index + 1

    if reference_index:
        if database_index:
            reference_rows = genome_property_record[reference_index:database_index]
        else:
            reference_rows = genome_property_record[reference_index:]

        references = parse_literature_references(reference_rows)
    else:
        references = []

    if database_index:
        if step_index:
            database_rows = genome_property_record[database_index:step_index - 1]
        else:
            database_rows = genome_property_record[database_index:]

        databases = parse_database_references(database_rows)
    else:
        databases = []

    if step_index:
        step_rows = genome_property_record[step_index:]
        steps = parse_steps(step_rows)
    else:
        steps = []

    new_genome_property = GenomeProperty(accession_id=gathered_core_genome_property_markers.get('AC'),
                                         name=gathered_core_genome_property_markers.get('DE'),
                                         property_type=gathered_core_genome_property_markers.get('TP'),
                                         threshold=gathered_core_genome_property_markers.get('TH'),
                                         parents=gathered_core_genome_property_markers.get('PN'),
                                         description=gathered_core_genome_property_markers.get('CC'),
                                         private_notes=gathered_core_genome_property_markers.get('**'),
                                         references=references,
                                         databases=databases,
                                         steps=steps)

    for step in new_genome_property.steps:
        step.parent = new_genome_property

    return new_genome_property


def parse_database_references(genome_property_record):
    """
    Parses database reference from a genome properties record.

    :param genome_property_record: A list of marker, content tuples representing genome property flat file lines.
    :return: A list of DatabaseReference objects.
    """
    database_reference_markers = ('DC', 'DR')

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


def parse_literature_references(genome_property_record):
    """
    Parses literature references from a genome properties record.

    :param genome_property_record: A list of marker, content tuples representing genome property flat file lines.
    :return: A list of LiteratureReference objects.
    """
    # A list of record markers related to literature references.
    literature_reference_markers = ('RN', 'RM', 'RT', 'RA', 'RL')

    literature_references = []
    current_literature_reference = {}
    for marker, content in genome_property_record:
        if marker in literature_reference_markers:
            if marker in current_literature_reference:
                literature_references.append(LiteratureReference(number=current_literature_reference.get('RN'),
                                                                 pubmed_id=current_literature_reference.get('RM'),
                                                                 title=current_literature_reference.get('RT'),
                                                                 authors=current_literature_reference.get('RA'),
                                                                 journal=current_literature_reference.get('RL')))
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
                                                     journal=current_literature_reference.get('RL')))
    return literature_references


def parse_steps(genome_property_record):
    """
    Parses steps from a genome properties record.

    :param genome_property_record: A list of marker, content tuples representing genome property flat file lines.
    :return: A list of Step objects.
    """
    step_markers = ('SN', 'ID', 'DN', 'RQ', 'EV', 'TG')
    steps = []
    current_step_markers = []
    step_number = 0
    for marker, content in genome_property_record:
        if marker in step_markers:
            if not marker == 'SN':
                current_step_markers.append((marker, content))
            else:
                if current_step_markers:
                    functional_elements = parse_functional_elements(current_step_markers)
                    steps.append(Step(number=step_number, functional_elements=functional_elements))
                    current_step_markers = []
                    step_number = int(content)
                else:
                    step_number = int(content)

    functional_elements = parse_functional_elements(current_step_markers)
    steps.append(Step(number=step_number, functional_elements=functional_elements))

    return steps


def parse_functional_elements(genome_property_record):
    """
    Parses functional_elements from a genome properties record.

    :param genome_property_record: A list of marker, content tuples representing genome property flat file lines.
    :return: A list of functional_element objects.
    """
    functional_element_markers = ('ID', 'DN', 'RQ')
    functional_elements = []
    current_functional_element = {}

    evidence_markers = ('EV', 'TG')
    current_evidence = []

    for marker, content in genome_property_record:
        if marker in functional_element_markers:
            if marker in current_functional_element:
                found_evidence = parse_evidences(current_evidence)
                current_evidence = []

                functional_elements.append(FunctionalElement(identifier=current_functional_element.get('ID'),
                                                             name=current_functional_element.get('DN'),
                                                             required=current_functional_element.get('RQ'),
                                                             evidence=found_evidence))

                current_functional_element = {marker: content}
            else:
                if marker == 'RQ':  # Required should true content is 1.
                    if int(content) == 1:
                        content = True
                    else:
                        content = False

                current_functional_element[marker] = content

        elif marker in evidence_markers:
            current_evidence.append((marker, content))
        else:
            continue  # Move on if marker is not a functional element marker or evidence marker.

    if current_evidence:
        evidence = parse_evidences(current_evidence)
    else:
        evidence = None

    functional_elements.append(FunctionalElement(identifier=current_functional_element.get('ID'),
                                                 name=current_functional_element.get('DN'),
                                                 required=current_functional_element.get('RQ'),
                                                 evidence=evidence))
    return functional_elements


def parse_evidences(genome_property_record):
    """
    Parses evidences from a genome properties record.

    :param genome_property_record: A list of marker, content tuples representing genome property flat file lines.
    :return: A list of evidence objects.
    """
    evidence_markers = ('EV', 'TG')
    evidences = []
    current_evidence = {}
    for marker, content in genome_property_record:
        if marker in evidence_markers:
            if marker in current_evidence:
                new_evidence = parse_single_evidence(current_evidence)

                evidences.append(new_evidence)
                current_evidence = {marker: content}
            else:
                if marker == 'EV' or marker == 'TG':
                    current_evidence[marker] = content

    new_evidence = parse_single_evidence(current_evidence)
    evidences.append(new_evidence)

    return evidences


def parse_single_evidence(current_evidence_dictionary):
    """
    The creates an Evidence object from a pair of EV and TG tag content strings.

    :param current_evidence_dictionary: A dictionary containing EV and TG to content string mappings.
    :return: An Evidence object.
    """
    evidence_string = current_evidence_dictionary.get('EV')
    gene_ontology_string = current_evidence_dictionary.get('TG')

    sufficient = False
    if evidence_string:
        evidence_identifiers = extract_identifiers(evidence_string)

        if 'sufficient' in evidence_string:
            sufficient = True
    else:
        evidence_identifiers = None

    if gene_ontology_string:
        gene_ontology_identifiers = extract_identifiers(gene_ontology_string)
    else:
        gene_ontology_identifiers = None

    new_evidence = Evidence(evidence_identifiers=evidence_identifiers,
                            gene_ontology_terms=gene_ontology_identifiers, sufficient=sufficient)
    return new_evidence


def extract_identifiers(identifier_string):
    """
    Parse database or Genprop identifiers from an EV or TG tag content string.

    :param identifier_string: The contents string from a EV or TG tag.
    :return: A list of identifiers.
    """
    split_content = filter(None, identifier_string.split(';'))
    cleaned_content = map(lambda evidence: evidence.strip(), split_content)
    identifiers = list([evidence for evidence in cleaned_content if evidence != 'sufficient'])
    return identifiers
