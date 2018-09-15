#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2018)

Description: The genome property tree class.
"""

from modules.genome_properties_tree import GenomePropertiesTree
from modules.genome_property import GenomeProperty
from modules.step import Step
import pandas as pd


class GenomePropertiesResults(object):
    """
    This class contains a representation of a table of results from one or more genome properties assignments.
    """

    def __init__(self, global_genome_properties_tree: GenomePropertiesTree, *genome_properties_results: dict):
        """

        :param global_genome_properties_tree: The global genome properties tree.
        :param genome_properties_results_dict: One or more parsed genome properties assignments.
        """

        property_tables = []
        step_tables = []
        sample_names = []
        for result in genome_properties_results:
            sample_names.append(result.pop('name'))
            property_table, step_table = create_assignment_tables(global_genome_properties_tree, result)
            property_tables.append(property_table)
            step_tables.append(step_table)

        combined_properties_table = pd.concat(property_tables, axis=1)
        combined_step_table = pd.concat(step_tables, axis=1)
        combined_properties_table.columns = sample_names
        combined_step_table.columns = sample_names

        self.tree = global_genome_properties_tree
        self.sample_names = sample_names
        self.property_results = combined_properties_table
        self.step_results = combined_step_table

    def get_property_result(self, genome_property_id):
        return self.property_results.loc[genome_property_id].tolist()

    def get_step_result(self, genome_property_id, step_number):
        return self.step_results.loc[genome_property_id].loc[step_number].tolist()

    def to_json(self):
        return {'sample_names': self.sample_names, 'property_tree': self.generate_json_tree(self.tree.root)}

    def generate_json_tree(self, genome_properties_root):
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
                             'name': genome_properties_root.name,
                             'enabled': False,
                             'result': self.get_step_result(genome_properties_root.id,
                                                            step.number)}
                children.append(step_dict)
        node_dict['children'] = children

        return node_dict


def create_assignment_tables(genome_properties_tree: GenomePropertiesTree, long_form_parser_results: dict):
    """
    Takes a results dictionary from the long form parser and creates two tables. One for property results and
    one for step results.

    :param genome_properties_tree: The global genome properties tree.
    :param long_form_parser_results: Per-sample genome properties results from the long form parser.
    :return: A tuple containing an property assignment table and step assignments table.
    """
    property_assignments = {}
    step_assignments = {}

    for genome_property_id, assignments in long_form_parser_results.items():

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

    assign_results_to_property_and_children(property_assignments, step_assignments, genome_properties_tree.root)

    property_table = pd.DataFrame.from_dict(property_assignments, orient='index', columns=['Property_Result'])
    property_table.index.names = ['Genome_Property_ID']

    step_table = pd.DataFrame(create_step_table_rows(step_assignments),
                              columns=['Genome_Property_ID', 'Step_Number', 'Step_Result'])
    step_table.set_index(['Genome_Property_ID', 'Step_Number'], inplace=True)

    return property_table, step_table


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
        required_values = [step_value for step_number, step_value in current_step_assignments.items() if
                           step_number in required_step_ids]
        genome_property_result = assign_property_result_from_required_steps(required_values, genome_property.threshold)
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


def assign_property_result_from_required_steps(child_assignment_results: list,
                                               threshold: int = 0):
    """
    Takes the assignment results from each step of a genome property and uses them to
    assign a result for the property itself.

    :param child_assignment_results: A list of assignment results for child steps or genome properties.
    :param threshold: The threshold of 'YES' assignments necessary for a 'PARTIAL' assignment.
    :return: The parents assignment result.
    """

    yes_count = child_assignment_results.count('YES')

    if yes_count == len(child_assignment_results):
        genome_property_result = 'YES'
    elif yes_count > threshold:
        genome_property_result = 'PARTIAL'
    else:
        genome_property_result = 'NO'

    return genome_property_result


def assign_result_from_child_assignment_results(child_assignment_results: list):
    """
    Takes the assignment results from each step of a genome property and uses them to
    assign a result for the property itself.

    :param child_assignment_results: A list of assignment results for child steps or genome properties.
    :return: The parents assignment result.
    """

    yes_count = child_assignment_results.count('YES')
    no_count = child_assignment_results.count('NO')

    if yes_count == len(child_assignment_results):
        genome_property_result = 'YES'
    elif no_count == len(child_assignment_results):
        genome_property_result = 'NO'
    else:
        genome_property_result = 'PARTIAL'

    return genome_property_result


def create_step_table_rows(step_assignments):
    for genome_property_id, step in step_assignments.items():
        for step_number, step_result in step.items():
            yield genome_property_id, step_number, step_result
