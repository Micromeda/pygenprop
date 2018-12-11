#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2018)

Description: The genome property tree class.
"""

import json
import pandas as pd
from pygenprop.step import Step
from pygenprop.tree import GenomePropertiesTree
from pygenprop.genome_property import GenomeProperty


class GenomePropertiesResults(object):
    """
    This class contains a representation of a table of results from one or more genome properties assignments.
    """

    def __init__(self, *genome_properties_results: dict, genome_properties_tree: GenomePropertiesTree):
        """
        Constructs the genome properties results object.

        :param genome_properties_tree: The global genome properties tree.
        :param genome_properties_results_dict: One or more parsed genome properties assignments.
        """

        property_tables = []
        step_tables = []
        sample_names = []
        for result in genome_properties_results:
            result_copy = result.copy()
            sample_names.append(result_copy.pop('sample_name'))
            property_table, step_table = create_assignment_tables(genome_properties_tree, result_copy)
            property_tables.append(property_table)
            step_tables.append(step_table)

        combined_properties_table = pd.concat(property_tables, axis=1)
        combined_step_table = pd.concat(step_tables, axis=1)
        combined_properties_table.columns = sample_names
        combined_step_table.columns = sample_names

        self.tree = genome_properties_tree
        self.sample_names = sample_names
        self.property_results = combined_properties_table
        self.step_results = combined_step_table

    def get_property_result(self, genome_property_id):
        """
        Gets the assignment results for a given genome property.

        :param genome_property_id: The id of the genome property to get results for.
        :return: A list containing the assignment results for the genome property in question.
        """
        return self.property_results.loc[genome_property_id].tolist()

    def get_step_result(self, genome_property_id, step_number):
        """
        Gets the assignment results for a given step of a genome property.

        :param genome_property_id: The id of the genome property that the step belongs too.
        :param step_number: The step number of the step.
        :return: A list containing the assignment results for the step in question.
        """
        return self.step_results.loc[genome_property_id].loc[step_number].tolist()

    def to_json(self, file_handle=None):
        """
        Returns a JSON representation of the step results.
        :return: A nested dict of the assignment results and sample names.
        """
        json_data = {'sample_names': self.sample_names, 'property_tree': self.generate_json_tree(self.tree.root)}

        if file_handle:
            json.dump(json_data, file_handle)
        else:
            return json.dumps(json_data)

    def generate_json_tree(self, genome_properties_root):
        """
        Creates a tree based representation of the genome properties assignment results.

        :param genome_properties_root: The root element of the genome properties tree.
        :return: A nested dict of assignment results.
        """
        node_dict = {'property_id': genome_properties_root.id,
                     'name': genome_properties_root.name,
                     'enabled': False,
                     'result': self.get_property_result(genome_properties_root.id)}
        children = []
        for step in genome_properties_root.steps:
            step_child_properties = step.genome_properties

            if step_child_properties:
                for child in step_child_properties:
                    children.append(self.generate_json_tree(child))
            else:
                step_dict = {'step_id': step.number,
                             'name': step.name,
                             'enabled': False,
                             'result': self.get_step_result(genome_properties_root.id,
                                                            step.number)}
                children.append(step_dict)
        node_dict['children'] = children

        return node_dict


def create_assignment_tables(genome_properties_tree: GenomePropertiesTree, long_form_parser_results: dict):
    """
    Takes a results dictionary from the long form parser and creates two tables. One for property results and
    one for step results. The longform results file has only leaf assignment results. We have to bootstrap the rest.

    :param genome_properties_tree: The global genome properties tree.
    :param long_form_parser_results: Per-sample genome properties results from the long form parser.
    :return: A tuple containing an property assignment table and step assignments table.
    """
    property_assignments = {}
    step_assignments = {}

    tree_identifiers = set(genome_property.id for genome_property in genome_properties_tree)
    filtered_parser_results = {identifier: long_form_parser_results[identifier] for identifier in tree_identifiers if identifier in long_form_parser_results.keys()}

    # Record the leaf assignments.
    for genome_property_id, assignments in filtered_parser_results.items():
        property_assignments[genome_property_id] = assignments['result']

        all_step_numbers = set(step.number for step in genome_properties_tree[genome_property_id].steps)
        supported_step_numbers = set(assignments['supported_steps'])
        unsupported_steps_numbers = all_step_numbers - supported_step_numbers

        current_genome_property_step_assignments = {}
        for step_number in supported_step_numbers:
            current_genome_property_step_assignments[step_number] = 'YES'

        for step_number in unsupported_steps_numbers:
            current_genome_property_step_assignments[step_number] = 'NO'

        step_assignments[genome_property_id] = current_genome_property_step_assignments

    # Bootstrap the other assignments from the leaf assignments.
    assign_results_to_property_and_children(property_assignments, step_assignments, genome_properties_tree.root)

    property_table = pd.DataFrame.from_dict(property_assignments, orient='index', columns=['Property_Result'])
    property_table.index.names = ['Genome_Property_ID']

    step_table = pd.DataFrame(create_step_table_rows(step_assignments),
                              columns=['Genome_Property_ID', 'Step_Number', 'Step_Result'])
    step_table.set_index(['Genome_Property_ID', 'Step_Number'], inplace=True)

    return property_table, step_table


def create_step_table_rows(step_assignments):
    """
    Unfolds a step result dict of dict and yields a step table row.

    :param step_assignments: A dict of dicts containing step assignment information ({gp_key -> {stp_key --> result}})
    """
    for genome_property_id, step in step_assignments.items():
        for step_number, step_result in step.items():
            yield genome_property_id, step_number, step_result


def assign_results_to_property_and_children(property_assignments: dict, step_assignments: dict,
                                            genome_property: GenomeProperty):
    """
    Recursively assigns a result to a genome property and its children.

    :param property_assignments: A dict containing the assignments of all currently assigned genome properties.
    :param step_assignments: A dict containing the assignments of all currently assigned genome property steps.
    :param genome_property: The genome property to assign the results to.
    :return: The assignment results for the genome property.
    """
    current_step_assignments = {}
    required_steps = genome_property.required_steps

    for step in genome_property.steps:
        current_step_assignments[step.number] = assign_step_result(property_assignments, step_assignments, step)

    if required_steps:
        required_step_ids = [step.number for step in required_steps]
        required_step_values = [step_value for step_number, step_value in current_step_assignments.items() if
                                step_number in required_step_ids]
        genome_property_result = assign_property_result_from_required_steps(required_step_values,
                                                                            genome_property.threshold)
    else:
        genome_property_result = assign_result_from_child_assignment_results(list(current_step_assignments.values()))

    genome_property_id = genome_property.id
    step_assignments[genome_property_id] = current_step_assignments
    property_assignments[genome_property_id] = genome_property_result

    return genome_property_result


def assign_step_result(property_assignments: dict, step_assignments: dict, step: Step):
    """
    Recursively assigns a result to a step and its children.

    :param property_assignments: A dict containing the assignments of all currently assigned genome properties.
    :param step_assignments: A dict containing the assignments of all currently assigned genome property steps.
    :param step: The step to assign the results to.
    :return: The assignment results for the step.
    """
    child_genome_properties = step.genome_properties
    cached_step_results_for_parent_genome_property = step_assignments.get(step.parent.id)

    if cached_step_results_for_parent_genome_property:
        cached_step_result = cached_step_results_for_parent_genome_property.get(step.number)
        if cached_step_result:
            current_step_result = cached_step_result
        else:
            current_step_result = 'NO'
    elif len(child_genome_properties) > 0:
        child_genome_property_assignments = []
        for child_property in child_genome_properties:
            child_genome_property_assignments.append(assign_results_to_property_and_children(property_assignments,
                                                                                             step_assignments,
                                                                                             child_property))

        current_step_result = assign_result_from_child_assignment_results(child_genome_property_assignments)
    else:
        current_step_result = 'NO'

    return current_step_result


def assign_property_result_from_required_steps(required_step_results: list, threshold: int = 0):
    """
    Takes the assignment results for each required step of a genome property and uses them to
    assign a result for the property itself. This is the classic algorithm used by EBI Genome Properties.

    From: https://genome-properties.readthedocs.io/en/latest/calculating.html

    To determine if the GP resolves to a YES (all required steps are present), NO (too few required steps are present)
    or PARTIAL (the number of required steps present is greater than the threshold, indicating that some evidence of
    the presence of the GP can be assumed).

    Child steps must be present ('YES') not partial.

    In Perl code for Genome Properties:

    Link: https://github.com/ebi-pf-team/genome-properties/blob/a76a5c0284f6c38cb8f43676618cf74f64634d33/code/pygenprop/GenomeProperties.pm#L646

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

    :param required_step_results: A list of assignment results for child steps or genome properties.
    :param threshold: The threshold of 'YES' assignments necessary for a 'PARTIAL' assignment.
    :return: The parent's assignment result.
    """
    yes_count = required_step_results.count('YES')

    if yes_count == len(required_step_results):
        genome_property_result = 'YES'
    elif yes_count > threshold:
        genome_property_result = 'PARTIAL'
    else:
        genome_property_result = 'NO'

    return genome_property_result


def assign_result_from_child_assignment_results(child_results: list):
    """
    Takes the assignment results from all child results and uses them to assign a result for the parent itself. This
    algorithm is used to assign results to a single step from child functional elements and for genome properties that
    have no required steps such as "category" type genome properties. This is a more generic version of the algorithm
    used in assign_property_result_from_required_steps()

    If all child assignments are No, parent should be NO.
    If all child assignments are Yes, parent should be YES.
    Any thing else in between, parents should be PARTIAL.

    :param child_results: A list of assignment results for child steps or genome properties.
    :return: The parents assignment result.
    """
    yes_count = child_results.count('YES')
    no_count = child_results.count('NO')

    if yes_count == len(child_results):
        genome_property_result = 'YES'
    elif no_count == len(child_results):
        genome_property_result = 'NO'
    else:
        genome_property_result = 'PARTIAL'

    return genome_property_result



