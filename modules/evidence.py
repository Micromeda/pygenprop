#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: The evidence class.
"""


class Evidence(object):
    """A piece of evidence (ex. InterPro HMM hit or GenProp) that supports the existence of a functional element."""

    def __init__(self, evidence_identifiers=None, gene_ontology_terms=None, sufficient=False):
        """
        Creates a new Evidence object.
        :param evidence_identifiers: A list of identifiers of proteins or processes supporting the existence of a
                                     FunctionalElement (i.e a list of Intro Consortium IDs or GenProp Accessions).
        :param gene_ontology_terms: The ids for gene ontology (GO) terms defining the protein or process supporting
                                    the existence of a FunctionalElement.
        :param sufficient: Can this evidence alone prove the existence of FunctionalElement?
        """

        if evidence_identifiers is None:
            evidence_identifiers = set
        if gene_ontology_terms is None:
            gene_ontology_terms = set
        if sufficient is None:
            sufficient = False

        self.evidence_identifiers = evidence_identifiers
        self.gene_ontology_terms = gene_ontology_terms
        self.sufficient = sufficient

    def __repr__(self):
        repr_data = ['Evidence_IDs: ' + str(self.evidence_identifiers),
                     'GO Terms: ' + str(self.gene_ontology_terms),
                     'Sufficient: ' + str(self.sufficient)]
        return '(' + ', '.join(repr_data) + ')'


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
    cleaned_content = set(map(lambda evidence: evidence.strip(), split_content))
    identifiers = set(evidence for evidence in cleaned_content if evidence != 'sufficient')
    return identifiers
