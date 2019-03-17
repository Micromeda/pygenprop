#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: Functions for assigning genome properties.
"""
from pygenprop.evidence import Evidence
from pygenprop.functional_element import FunctionalElement
from pygenprop.genome_property import GenomeProperty
from pygenprop.step import Step


class AssignmentCache(object):
    """
    This class contains a representation of precomputed assignment results and InterPro member database matches.
    """

    def __init__(self, interpro_member_database_identifiers: list = None, sample_name=None):
        if interpro_member_database_identifiers:
            interpro_member_database_identifiers = set(interpro_member_database_identifiers)

        self.property_assignments = {}
        self.step_assignments = {}
        self.interpro_member_database_identifiers = interpro_member_database_identifiers
        self.sample_name = sample_name

    def cache_property_assignment(self, genome_property_identifier: str, assignment: str):
        """
        Stores cached assignment results for a genome property.

        :param genome_property_identifier: The identifier of genome property.
        :param assignment: An assignment of YES, NO or PARTIAL for the given genome property.
        """
        self.property_assignments[genome_property_identifier] = assignment

    def get_property_assignment(self, genome_property_identifier):
        """
        Retrieves cached assignment results for a genome property.

        :param genome_property_identifier: The identifier of genome property.
        :return: An assignment of YES, NO or PARTIAL for the given genome property.
        """
        return self.property_assignments.get(genome_property_identifier)

    def cache_step_assignment(self, genome_property_identifier: str, step_number: int, assignment: str):
        """
        Stores cached assignment results for a genome property step.

        :param genome_property_identifier: The identifier of the genome property for which the step belongs.
        :param step_number: The steps number.
        :param assignment: An assignment of YES or NO for the given step.
        """
        parent_genome_property_step_assignments = self.step_assignments.get(genome_property_identifier)

        if parent_genome_property_step_assignments:
            parent_genome_property_step_assignments[step_number] = assignment
        else:
            self.step_assignments[genome_property_identifier] = {step_number: assignment}

    def get_step_assignment(self, genome_property_identifier: str, step_number: int):
        """
        Retrieves cached assignment results for a genome property step.

        :param genome_property_identifier: The identifier of the genome property for which the step belongs.
        :param step_number: The steps number.
        :return: An assignment of YES or NO for the given step.
        """
        parent_genome_property_step_results = self.step_assignments.get(genome_property_identifier)

        if parent_genome_property_step_results:
            found_step_assignment = parent_genome_property_step_results.get(step_number)
            if found_step_assignment:
                cached_step_assignment = found_step_assignment
            else:
                cached_step_assignment = None
        else:
            cached_step_assignment = None

        return cached_step_assignment

    def flush_property_from_cache(self, genome_property_identifier):
        """
        Remove a genome property from the cache using its identifier.

        :param genome_property_identifier: The identifier of the property to remove from the cache.
        """
        self.property_assignments.pop(genome_property_identifier, None)
        self.step_assignments.pop(genome_property_identifier, None)

    @property
    def genome_property_identifiers(self):
        """
        Creates a set of identifiers belonging to the genome properties cached.

        :return: A set of genome property identifiers.
        """
        return list(self.property_assignments.keys())


def assign_genome_property(assignment_cache: AssignmentCache, genome_property: GenomeProperty):
    """
    Recursively assigns a result to a genome property and its children.

    :param assignment_cache: A cache containing step and property assignments and InterPro member database matches.
    :param genome_property: The genome property to assign the results to.
    :return: The assignment results for the genome property.
    """

    current_step_assignments = {}
    required_steps = genome_property.required_steps

    for step in genome_property.steps:
        current_step_assignments[step.number] = assign_step(assignment_cache, step)

    if required_steps:
        required_step_numbers = [step.number for step in required_steps]
        required_step_values = [step_value for step_number, step_value in current_step_assignments.items() if
                                step_number in required_step_numbers]
        genome_property_assignment = calculate_property_assignment_from_required_steps(required_step_values,
                                                                                       genome_property.threshold)
    else:
        genome_property_assignment = calculate_property_assignment_from_all_steps(
            list(current_step_assignments.values()))

    assignment_cache.cache_property_assignment(genome_property.id, genome_property_assignment)

    return genome_property_assignment


def assign_step(assignment_cache: AssignmentCache, step: Step):
    """
    Assigns a result (YES, NO) to a functional element based on assignments of its functional elements.

    :param assignment_cache: A cache containing step and property assignments and InterPro member database matches.
    :param step: The current step element which needs assignment.
    :return: The assignment for the step.
    """
    functional_elements = step.functional_elements

    functional_element_assignments = []
    for element in functional_elements:
        element_assignment = assign_functional_element(assignment_cache, element)
        functional_element_assignments.append(element_assignment)

    step_assignment = calculate_step_or_functional_element_assignment(functional_element_assignments,
                                                                      sufficient_scheme=True)

    assignment_cache.cache_step_assignment(step.parent.id, step.number, step_assignment)

    return step_assignment


def assign_functional_element(assignment_cache: AssignmentCache, functional_element: FunctionalElement):
    """
    Assigns a result (YES, NO) to a functional element based on assignments of its evidences.

    :param assignment_cache: A cache containing step and property assignments and InterPro member database matches.
    :param functional_element: The current functional_element which needs assignment.
    :return: The assignment for the functional element.
    """

    element_evidences = functional_element.evidence

    evidence_assignments_and_sufficients = []
    for current_evidence in element_evidences:
        evidence_assignment = assign_evidence(assignment_cache, current_evidence)

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


def assign_evidence(assignment_cache: AssignmentCache, current_evidence: Evidence):
    """
    Assigns a result (YES, NO) to a evidence based of the presence or absence of InterPro member identifiers or
    the assignment of evidence child genome properties.

    :param assignment_cache: A cache containing step and property assignments and InterPro member database matches.
    :param current_evidence: The current evidence which needs assignment.
    :return: The assignment for the evidence.
    """

    if current_evidence.has_genome_property:
        primary_genome_property = current_evidence.genome_properties[0]
        primary_property_identifier = primary_genome_property.id
        cached_property_assignment = assignment_cache.get_property_assignment(primary_property_identifier)

        if cached_property_assignment:
            evidence_assignment = cached_property_assignment
        else:
            evidence_genome_property_assignment = assign_genome_property(assignment_cache, primary_genome_property)
            evidence_assignment = evidence_genome_property_assignment
    else:
        unique_interpro_member_identifiers = assignment_cache.interpro_member_database_identifiers
        if unique_interpro_member_identifiers:
            if unique_interpro_member_identifiers.isdisjoint(set(current_evidence.evidence_identifiers)):
                evidence_assignment = 'NO'
            else:
                evidence_assignment = 'YES'
        else:
            evidence_assignment = 'NO'

    return evidence_assignment


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
