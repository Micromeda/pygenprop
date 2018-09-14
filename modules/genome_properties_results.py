#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2018)

Description: The genome property tree class.
"""

import json

import pandas as pd

from modules.genome_properties_tree import GenomePropertiesTree
from modules.step import Step


class GenomePropertiesResults(object):
    """
    This class contains a representation of a table of results from one or more genome properties assignments.
    """

    def __init__(self, global_genome_properties_tree: GenomePropertiesTree, *genome_properties_results: dict):
        """

        :param global_genome_properties_tree:
        :param genome_properties_results_dict:
        """

        self.tree = global_genome_properties_tree

        for sample_result in genome_properties_results:
            json_string = json.dumps(sample_result)
            # data =


def assign_genome_properties(genome_properties_tree: GenomePropertiesTree, genome_property_assignments: dict,
                             global_step_assignments: dict, genome_property_id: str = None):
    if genome_property_id:
        current_genome_property = genome_properties_tree[genome_property_id]
    else:
        current_genome_property = genome_properties_tree.root

    current_step_assignments = {}
    for step in current_genome_property.steps:
        step_number = step.number

        current_step_result = assign_step_result(genome_properties_tree, genome_property_assignments,
                                                 global_step_assignments, step, genome_property_id)

        current_step_assignments[step_number] = current_step_result

    current_step_assignment_values = list(current_step_assignments.values())
    property_threshold = current_genome_property.threshold

    genome_property_result = assign_genome_property_result(current_step_assignment_values,
                                                           property_threshold)

    global_step_assignments[genome_property_id] = current_step_assignments
    genome_property_assignments[genome_property_id] = genome_property_result

    return genome_property_result


def assign_step_result(genome_properties_tree: GenomePropertiesTree, genome_property_assignments: dict,
                       global_step_assignments: dict, step: Step, genome_property_id: str):

    if genome_property_id in global_step_assignments:
        current_step_result = global_step_assignments[genome_property_id][step.number]
    elif len(step.genome_property_identifiers) > 0:
        current_step_result = assign_step_result_from_child_genome_properties(genome_properties_tree,
                                                                              genome_property_assignments,
                                                                              global_step_assignments,
                                                                              step)
    else:
        current_step_result = False

    return current_step_result


def assign_step_result_from_child_genome_properties(genome_properties_tree, genome_property_assignments,
                                                    global_step_assignments, step):
    current_step_result = False
    for element in step.functional_elements:
        functional_element_results = []
        for evidence in element.evidence:
            if evidence.has_genome_property:
                for child_genome_property_id in evidence.genome_property_identifiers:

                    if child_genome_property_id in genome_property_assignments:
                        current_step_result = genome_property_assignments[child_genome_property_id]
                        functional_element_results.append(current_step_result)
                    else:
                        child_genome_property_result = assign_genome_properties(genome_properties_tree,
                                                                                genome_property_assignments,
                                                                                global_step_assignments,
                                                                                child_genome_property_id)

                        functional_element_results.append(child_genome_property_result)
        if 'NO' in functional_element_results:
            current_step_result = False
        else:
            current_step_result = True

    return current_step_result


def assign_genome_property_result(current_step_assignment_values, property_threshold):
    """
    Takes the assignment results from each step of a genome property and uses them to
    assign a result for the property itself.

    :param current_step_assignment_values: A list of assignment results for each step of a genome property.
    :param property_threshold: The threshold of a genome property.
    :return: The assignment result for the genome property.
    """
    true_count = current_step_assignment_values.count(True)

    if true_count == len(current_step_assignment_values):
        genome_property_result = 'YES'
    elif true_count > property_threshold:
        genome_property_result = 'PARTIAL'
    else:
        genome_property_result = 'NO'

    return genome_property_result
