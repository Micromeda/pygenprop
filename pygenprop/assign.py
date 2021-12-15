#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: Functions for assigning genome properties.
"""

import pandas as pd

from pygenprop.evidence import Evidence
from pygenprop.functional_element import FunctionalElement
from pygenprop.genome_property import GenomeProperty
from pygenprop.step import Step
from pygenprop.tree import GenomePropertiesTree


class AssignmentCache(object):
    """
    This class contains a representation of precomputed assignment results and InterPro member database matches.
    """

    def __init__(self, interpro_signature_accessions: list = None, sample_name=None):
        """
        Constructs an assignment cache object.

        :param sample_name: The name of the sample
        :param interpro_signature_accessions: A set of InterPro signature accessions found in an organism's InterProScan
                                              annotation file.
        """
        if interpro_signature_accessions:
            interpro_signature_accessions = set(interpro_signature_accessions)

        self.property_assignments = {}
        self.step_assignments = {}
        self.interpro_signature_accessions = interpro_signature_accessions
        self.sample_name = sample_name

    @property
    def property_identifiers(self):
        """
        Creates a set of identifiers belonging to the genome properties cache.

        :return: A set of genome property identifiers.
        """

        return set(self.property_assignments.keys())

    @property
    def property_identifiers_of_step_cache(self):
        """
        Creates a set of identifiers belonging to the step assignment cache.

        :return: A set of genome property identifiers.
        """
        return set(self.step_assignments.keys())

    @property
    def unsynchronized_identifiers(self):
        """
        Provides a set of genome property identifiers which are not shared between step and property assignments.

        :return: The set of unsynchronized identifiers
        """
        return self.property_identifiers - self.property_identifiers_of_step_cache

    def cache_property_assignment(self, property_identifier: str, assignment: str):
        """
        Stores cached assignment results for a genome property.

        :param property_identifier: The identifier of genome property.
        :param assignment: An assignment of YES, NO or PARTIAL for the given genome property.
        """
        self.property_assignments[property_identifier] = assignment

    def get_property_assignment(self, property_identifier):
        """
        Retrieves cached assignment results for a genome property.

        :param property_identifier: The identifier of genome property.
        :return: An assignment of YES, NO or PARTIAL for the given genome property.
        """
        return self.property_assignments.get(property_identifier)

    def cache_step_assignment(self, property_identifier: str, step_number: int, assignment: str):
        """
        Stores cached assignment results for a genome property step.

        :param property_identifier: The identifier of the genome property for which the step belongs.
        :param step_number: The steps number.
        :param assignment: An assignment of YES or NO for the given step.
        """
        parent_genome_property_step_assignments = self.step_assignments.get(property_identifier)

        if parent_genome_property_step_assignments:
            parent_genome_property_step_assignments[step_number] = assignment
        else:
            self.step_assignments[property_identifier] = {step_number: assignment}

    def get_step_assignment(self, property_identifier: str, step_number: int):
        """
        Retrieves cached assignment results for a genome property step.

        :param property_identifier: The identifier of the genome property for which the step belongs.
        :param step_number: The steps number.
        :return: An assignment of YES or NO for the given step.
        """
        parent_genome_property_step_results = self.step_assignments.get(property_identifier)

        if parent_genome_property_step_results:
            found_step_assignment = parent_genome_property_step_results.get(step_number)
            if found_step_assignment:
                cached_step_assignment = found_step_assignment
            else:
                cached_step_assignment = None
        else:
            cached_step_assignment = None

        return cached_step_assignment

    def flush_property_from_cache(self, property_identifier):
        """
        Remove a genome property from the cache using its identifier.

        :param property_identifier: The identifier of the property to remove from the cache.
        """
        self.property_assignments.pop(property_identifier, None)
        self.step_assignments.pop(property_identifier, None)

    def bootstrap_assignments(self, properties_tree: GenomePropertiesTree):
        """
        Recursively fills in assignments for all genome properties in the genome properties tree based of existing
        cached assignments and InterPro member database identifiers.

        :param self: A cache containing step and property assignments and InterPro member database matches.
        :param properties_tree: The global genome properties tree
        :return: A completed assignment cache with assignments for all genome properties and properties steps.
        """
        self.synchronize_with_tree(properties_tree)

        # Bootstrap the other assignments from the leaf assignments.
        self.bootstrap_assignments_from_genome_property(properties_tree.root)
        self.bootstrap_missing_step_assignments(properties_tree)

    def bootstrap_missing_step_assignments(self, properties_tree: GenomePropertiesTree):
        """
        In some cases, such as when opening up assignment caches where steps that have been assigned NO have been
        removed, we need to bootstrap step assignments back into existence.

        :param self: A cache containing step and property assignments and InterPro member database matches.
        :param properties_tree: The global genome properties tree
        """

        # The identifiers of properties with no step assignments.
        property_identifiers_not_in_step_cache = self.unsynchronized_identifiers

        # Bootstrap step assignments for properties
        for property_identifier in property_identifiers_not_in_step_cache:
            for step in properties_tree[property_identifier].steps:
                self.bootstrap_assignments_from_step(step)

        # Ensure that all steps have an assignment.
        all_missing_steps = []
        for property_identifier in self.property_identifiers:
            property_steps_from_tree = properties_tree[property_identifier].steps
            property_steps_from_cache = self.step_assignments[property_identifier]

            # If there are missing steps for this genome property in the cache.
            if len(property_steps_from_tree) != len(property_steps_from_cache):
                tree_step_numbers = {step.number for step in property_steps_from_tree}
                cached_step_numbers = set(property_steps_from_cache.keys())
                missing_step_numbers = tree_step_numbers - cached_step_numbers
                missing_property_steps = [step for step in property_steps_from_tree
                                          if step.number in missing_step_numbers]

                all_missing_steps.extend(missing_property_steps)

        for step in all_missing_steps:
            self.bootstrap_assignments_from_step(step)

    def bootstrap_assignments_from_genome_property(self, genome_property: GenomeProperty):
        """
        Recursively assigns a result to a genome property and its children.
    
        :param self: A cache containing step and property assignments and InterPro member database matches.
        :param genome_property: The genome property to assign the results to.
        :return: The assignment results for the genome property.
        """

        current_step_assignments = {}
        required_steps = genome_property.required_steps
        cached_property_assignment = self.get_property_assignment(genome_property.id)

        if cached_property_assignment:
            genome_property_assignment = cached_property_assignment
        else:
            for step in genome_property.steps:
                current_step_assignments[step.number] = self.bootstrap_assignments_from_step(step)

            if required_steps:
                required_step_numbers = [step.number for step in required_steps]
                required_step_values = [step_value for step_number, step_value in current_step_assignments.items() if
                                        step_number in required_step_numbers]
                genome_property_assignment = calculate_property_assignment_from_required_steps(required_step_values,
                                                                                               genome_property.threshold)
            else:
                genome_property_assignment = calculate_property_assignment_from_all_steps(
                    list(current_step_assignments.values()))

            self.cache_property_assignment(genome_property.id, genome_property_assignment)

        return genome_property_assignment

    def bootstrap_assignments_from_step(self, step: Step):
        """
        Assigns a result (YES, NO) to a functional element based on assignments of its functional elements.
    
        :param self: A cache containing step and property assignments and InterPro member database matches.
        :param step: The current step element which needs assignment.
        :return: The assignment for the step.
        """

        property_identifier = step.parent.id
        cached_step_assignment = self.get_step_assignment(property_identifier, step.number)

        if cached_step_assignment:
            step_assignment = cached_step_assignment
        else:
            functional_elements = step.functional_elements

            functional_element_assignments = []
            for element in functional_elements:
                element_assignment = self.bootstrap_assignments_from_functional_element(element)
                functional_element_assignments.append(element_assignment)

            step_assignment = calculate_step_or_functional_element_assignment(functional_element_assignments,
                                                                              sufficient_scheme=True)

            self.cache_step_assignment(step.parent.id, step.number, step_assignment)

        return step_assignment

    def bootstrap_assignments_from_functional_element(self, functional_element: FunctionalElement):
        """
        Assigns a result (YES, NO) to a functional element based on assignments of its evidences.

        :param self: A cache containing step and property assignments and InterPro member database matches.
        :param functional_element: The current functional_element which needs assignment.
        :return: The assignment for the functional element.
        """

        element_evidences = functional_element.evidence

        evidence_assignments_and_sufficients = []
        for current_evidence in element_evidences:
            evidence_assignment = self.bootstrap_assignments_from_evidence(current_evidence)

            sufficient = current_evidence.sufficient

            evidence_assignments_and_sufficients.append((evidence_assignment, sufficient))

        sufficient_evidence_assignments = [assignment for assignment, sufficient in evidence_assignments_and_sufficients
                                           if sufficient]

        if sufficient_evidence_assignments:
            sufficient_assignment = calculate_step_or_functional_element_assignment(sufficient_evidence_assignments,
                                                                                    sufficient_scheme=True)
            if sufficient_assignment == 'YES':
                functional_element_assignment = 'YES'
            else:
                functional_element_assignment = 'NO'
        else:
            evidence_assignments = [assignment for assignment, sufficient in evidence_assignments_and_sufficients]
            functional_element_assignment = calculate_step_or_functional_element_assignment(evidence_assignments)

        return functional_element_assignment

    def bootstrap_assignments_from_evidence(self, current_evidence: Evidence):
        """
        Assigns a result (YES, NO) to a evidence based of the presence or absence of InterPro member identifiers or
        the assignment of evidence child genome properties.

        :param current_evidence: The current evidence which needs assignment.
        :return: The assignment for the evidence.
        """

        if current_evidence.has_genome_property:
            primary_genome_property = current_evidence.genome_properties[0]
            evidence_assignment = self.bootstrap_assignments_from_genome_property(primary_genome_property)
        else:
            unique_interpro_member_identifiers = self.interpro_signature_accessions
            if unique_interpro_member_identifiers:
                if unique_interpro_member_identifiers.isdisjoint(set(current_evidence.evidence_identifiers)):
                    evidence_assignment = 'NO'
                else:
                    evidence_assignment = 'YES'
            else:
                evidence_assignment = 'NO'

        return evidence_assignment

    def synchronize_with_tree(self, properties_tree: GenomePropertiesTree):
        """
        Remove genome properties from the assignment cache that are not found in both the genome properties tree and
        the assignment cache. This prevents situations where different versions of the cache and tree cannot find each
        others genome properties.

        :param properties_tree: The global genome properties tree.
        :return: An assignment cache containing data for genome properties shared between the tree and cache.
        """

        unshared_identifiers = self.get_unshared_identifiers(properties_tree)

        for identifier in unshared_identifiers:
            self.flush_property_from_cache(identifier)

    def get_unshared_identifiers(self, properties_tree: GenomePropertiesTree):
        """
        Gets genome properties from the assignment cache that are not found in both the genome properties tree and
        the assignment cache. This prevents situations where different versions of the cache and tree cannot find each
        others genome properties.

        :param properties_tree: The global genome properties tree.
        :return: A set of identifiers not shared between the tree and assignment cache.
        """
        tree_identifiers = properties_tree.genome_property_identifiers
        assignment_cache_identifiers = self.property_identifiers
        return assignment_cache_identifiers - tree_identifiers

    def create_results_tables(self, properties_tree: GenomePropertiesTree):
        """
        Takes a results dictionary from the long form parser and creates two tables. One for property results and
        one for step results. The longform results file has only leaf assignment results. We have to bootstrap the rest.

        :param properties_tree: The global genome properties tree.
        :param self: Per-sample genome properties results from the long form parser.
        :return: A tuple containing an property assignment table and step assignments table.
        """

        # Take known assignments and matched InterPro member database
        # identifiers and calculate assignments for all properties.
        self.bootstrap_assignments(properties_tree)

        property_table = pd.DataFrame.from_dict(self.property_assignments,
                                                orient='index', columns=['Property_Result'])
        property_table.index.names = ['Property_Identifier']

        step_table = pd.DataFrame(self.create_step_table_rows(self.step_assignments),
                                  columns=['Property_Identifier', 'Step_Number', 'Step_Result'])
        step_table.set_index(['Property_Identifier', 'Step_Number'], inplace=True)

        return property_table, step_table

    @staticmethod
    def create_step_table_rows(step_assignments):
        """
        Unfolds a step result dict of dict and yields a step table row.

        :param step_assignments: A dict of dicts containing step assignment information ({gp_key -> {stp_key --> result}})
        """
        for genome_property_id, step in step_assignments.items():
            for step_number, step_result in step.items():
                yield genome_property_id, step_number, step_result

    def __repr__(self):
        if self.property_assignments:
            property_assignments = len(self.property_assignments)
        else:
            property_assignments = None

        if self.step_assignments:
            step_assignments = len(self.step_assignments)
        else:
            step_assignments = None

        if self.interpro_signature_accessions:
            interpro_identifiers = len(self.interpro_signature_accessions)
        else:
            interpro_identifiers = None

        repr_data = [str(self.sample_name),
                     'Property Assignments: ' + str(property_assignments),
                     'Step Assignments: ' + str(step_assignments),
                     'InterPro Identifiers: ' + str(interpro_identifiers),
                     'Unsynchronized Identifiers: ' + str(len(self.unsynchronized_identifiers))]
        return ', '.join(repr_data)


class AssignmentCacheWithMatches(AssignmentCache):
    """
    This class contains a representation of precomputed assignment results and InterPro member database matches.
    It also contains InterProScan and FASTA sequences supporting these assignments.
    """

    def __init__(self, match_info_frame=None, sequence_frame=None, sample_name=None):
        """
        Constructs the extended genome properties results object.

        :param match_info_frame: A pandas dataframe containing match information.
        :param sequence_frame: A panadas dataframe containing sequence information
        """
        if match_info_frame is None or sequence_frame is None:
            identifiers = None
            self.matches = None
        else:
            self.matches = match_info_frame.merge(sequence_frame, left_on='Protein_Accession',
                                                  right_on='Protein_Accession',
                                                  copy=False).drop_duplicates().set_index('Signature_Accession')

            identifiers = match_info_frame['Signature_Accession'].tolist()

        AssignmentCache.__init__(self, interpro_signature_accessions=identifiers, sample_name=sample_name)


def calculate_property_assignment_from_required_steps(required_step_assignments: list, threshold: int = 0):
    """
    Takes the assignment results for each required step of a genome property and uses them to
    assign a result for the property itself. This is the classic algorithm used by EBI Genome Properties.

    From: https://genome-properties.readthedocs.io/en/latest/calculating.html

    To determine if the GP resolves to a YES (all required steps are present), NO (too few required steps are present)
    or PARTIAL (the number of required steps present is greater than the threshold, indicating that some evidence of
    the presence of the GP can be assumed).

    Child steps must be present ('YES') not partial.

    In Perl code for Genome Properties:

    Link: https://github.com/ebi-pf-team/genome-properties/blob/
    a76a5c0284f6c38cb8f43676618cf74f64634d33/code/pygenprop/GenomeProperties.pm#L646

        #Three possible results for the evaluation
        if($found == 0 or $found <= $def->threshold){
            $def->result('NO'); #No required steps found
        }elsif($missing){
            $def->result('PARTIAL'); #One or more required steps found, but one or more required steps missing
        }else{
            $def->result('YES'); #All steps found.
        }

    If no required steps are found or the number found is less than or equal to the threshold --> No
    Else if any are missing --> PARTIAL
    ELSE (none are missing) --> YES

    So for problem space ALL_PRESENT > THRESHOLD > NONE_PRESENT:

    YES when ALL_PRESENT = CHILD_YES_COUNT
    PARTIAL when CHILD_YES_COUNT > THRESHOLD
    NO when CHILD_YES_COUNT <= THRESHOLD

    :param required_step_assignments: A list of assignment results for child steps or genome properties.
    :param threshold: The threshold of 'YES' assignments necessary for a 'PARTIAL' assignment.
    :return: The parent's assignment result.
    """
    yes_count = required_step_assignments.count('YES')

    if yes_count == len(required_step_assignments):
        genome_property_result = 'YES'
    elif yes_count > threshold:
        genome_property_result = 'PARTIAL'
    else:
        genome_property_result = 'NO'

    return genome_property_result


def calculate_property_assignment_from_all_steps(child_assignments: list):
    """
    Takes the assignment results from all child results and uses them to assign a result for the parent itself. This
    algorithm is used to assign results to a single step from child functional elements and for genome properties that
    have no required steps such as "category" type genome properties. This is a more generic version of the algorithm
    used in assign_property_result_from_required_steps()

    If all child assignments are No, parent should be NO.
    If all child assignments are Yes, parent should be YES.
    Any thing else in between, parents should be PARTIAL.

    :param child_assignments: A list of assignment results for child steps or genome properties.
    :return: The parents assignment result.
    """
    yes_count = child_assignments.count('YES')
    no_count = child_assignments.count('NO')

    if yes_count == len(child_assignments):
        genome_property_result = 'YES'
    elif no_count == len(child_assignments):
        genome_property_result = 'NO'
    else:
        genome_property_result = 'PARTIAL'

    return genome_property_result


def calculate_step_or_functional_element_assignment(child_assignments: list, sufficient_scheme=False):
    """
    Assigns a step result or functional element result based of the assignments of its children. In the case of steps,
    this would be functional element assignments. In the case of functional elements this would be evidences.

    For assignments from child genome properties YES or PARTIAL is considered YES.

    See: https://github.com/ebi-pf-team/genome-properties/blob/
    a76a5c0284f6c38cb8f43676618cf74f64634d33/code/modules/GenomeProperties.pm#L686

    if($evObj->gp){
        if(defined($self->get_defs->{ $evObj->gp })){
          # For properties a PARTIAL or YES result is considered success
          if( $self->get_defs->{ $evObj->gp }->result eq 'YES' or
              $self->get_defs->{ $evObj->gp }->result eq 'PARTIAL' ){
              $succeed++;
           }elsif($self->get_defs->{ $evObj->gp }->result eq 'UNTESTED'){
              $step->evaluated(0);

    :param sufficient_scheme: If false, any child NOs mean NO. If true, any child YES/PARTIAL means YES
    :param child_assignments: A list containing strings of YES, NO or PARTIAL
    :return: The assignment as either YES or NO.
    """
    no_count = child_assignments.count('NO')

    # Given a list of sufficient evidences, any could be PARTIAL or YES and the result would be YES.
    if sufficient_scheme:
        if no_count < len(child_assignments):
            result = 'YES'
        else:
            result = 'NO'
    # Given a list of non-sufficient evidences, all evidences have to be YES or PARTIAL or the result would be NO.
    else:
        if no_count == 0:
            result = 'YES'
        else:
            result = 'NO'

    return result
