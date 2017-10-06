#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: The step class.
"""


class Step(object):
    """A class representing a step that supports the existence of a genome property."""

    def __init__(self, number, identifier, name, gene_ontology_id=None, evidence=None, required=False,
                 sufficient=False):
        """
        Creates a new Step object.
        :param number: The position of the step in the step list.
        :param identifier: The identifier of the step.
        :param name: The name of the step.
        :param evidence: A list of identifiers of proteins or processes supporting this step
                        (i.e a list of Intro Consortium IDs or GenProp Accessions).
        :param gene_ontology_id: The id for gene ontology (GO) term of the protein supporting this step.
        :param required: Is this a required step for this genome property?
        :param sufficient: IS this step sufficient? (TODO: figure out what this means?)
        """

        if evidence is None:
            evidence = set
        if gene_ontology_id is None:
            gene_ontology_id = set

        self.number = int(number)
        self.id = identifier
        self.name = name
        self.evidence = evidence
        self.gene_ontology_id = gene_ontology_id
        self.required = required
        self.sufficient = sufficient

    def __repr__(self):
        repr_data = ['Step ' + str(self.number),
                     'ID: ' + str(self.id),
                     'Name: ' + str(self.name),
                     'Evidences: ' + str(self.evidence),
                     'Gene Ontology IDs: ' + str(self.gene_ontology_id),
                     'Required: ' + str(self.required),
                     'Sufficient: ' + str(self.sufficient)]
        return ', '.join(repr_data)


def parse_steps(genome_property_record):
    """
    Parses steps from a genome properties record.
    :param genome_property_record: A list of marker, content tuples representing genome property flat file lines.
    :return: A list of Step objects.
    """
    step_markers = ['SN', 'ID', 'DN', 'RQ', 'EV', 'TG']
    steps = []
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
                      gene_ontology_id=current_step.get('TG'), required=current_step.get('RQ'),
                      sufficient=current_step.get('SF')))

    return steps
