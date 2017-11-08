#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: The evidence class.
"""


class Evidence(object):
    """A piece of evidence (ex. InterPro HMM hit) that supports the existence of a functional element."""

    def __init__(self, evidence_ids=None, gene_ontology_ids=None, sufficient=False):
        """
        Creates a new Evidence object.
        :param evidence_ids: A list of identifiers of proteins or processes supporting the existence of a
                                FunctionalElement (i.e a list of Intro Consortium IDs or GenProp Accessions).
        :param gene_ontology_ids: The ids for gene ontology (GO) terms defining the protein or process supporting
                                    the existence of a FunctionalElement.
        :param sufficient: Can this step alone prove the existence of FunctionalElement?
        """

        if evidence_ids is None:
            evidence_ids = set
        if gene_ontology_ids is None:
            gene_ontology_ids = set
        if sufficient is None:
            sufficient = False

        self.evidence_ids = evidence_ids
        self.gene_ontology_ids = gene_ontology_ids
        self.sufficient = sufficient

    def __repr__(self):
        repr_data = ['Evidences IDs: ' + str(self.evidence_ids),
                     'Gene Ontology IDs: ' + str(self.gene_ontology_ids),
                     'Sufficient: ' + str(self.sufficient)]
        return ', '.join(repr_data)


def parse_evidence(genome_property_record):
    """
    Parses steps from a genome properties record.
    :param genome_property_record: A list of marker, content tuples representing genome property flat file lines.
    :return: A list of Step objects.
    """
    step_markers = ('SN', 'ID', 'DN', 'RQ', 'EV', 'TG')
    steps = []
    current_step = {}
    for marker, content in genome_property_record:
        if marker in step_markers:
            if marker in current_step:
                steps.append(FunctionalElement(number=current_step.get('SN'), identifier=current_step.get('ID'),
                                               name=current_step.get('DN'), evidence=current_step.get('EV'),
                                               gene_ontology_ids=current_step.get('TG'),
                                               required=current_step.get('RQ'),
                                               sufficient=current_step.get('SF')))

                if marker == 'SN':
                    content = int(content)

                current_step = {marker: content}
            else:
                if marker == 'SN':
                    content = int(content)
                elif marker == 'EV' or marker == 'TG':
                    split_content = filter(None, content.split(';'))
                    cleaned_content = set(map(lambda evidence: evidence.strip(), split_content))
                    if marker == 'EV':
                        if 'sufficient' in cleaned_content:
                            current_step['SF'] = True
                        else:
                            current_step['SF'] = False

                        content = set(evidence for evidence in cleaned_content if evidence != 'sufficient')
                    else:
                        content = cleaned_content
                elif marker == 'RQ':
                    if int(content) == 1:
                        content = True
                    else:
                        content = False

                current_step[marker] = content

    steps.append(Step(number=current_step.get('SN'), identifier=current_step.get('ID'),
                      name=current_step.get('DN'), evidence=current_step.get('EV'),
                      gene_ontology_ids=current_step.get('TG'), required=current_step.get('RQ'),
                      sufficient=current_step.get('SF')))

    return steps