#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2018)

Description: The genome property tree class.
"""

import json

import pandas as pd

from modules.genome_properties_tree import GenomePropertiesTree


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
                             global_step_assignments: dict, genome_property_id: str):

    current_genome_property = genome_properties_tree[genome_property_id]

    current_step_assignments = {}
    for step in current_genome_property.steps:
        current_step_result = False

        step_number = step.number
        if genome_property_id in global_step_assignments:
            current_step_result = global_step_assignments[genome_property_id][step_number]
        elif len(step.genome_property_identifiers) > 0:
            for element in step.functional_elements:
                functional_element_results = []
                for evidence in element.evidence:
                    if evidence.has_genome_property:
                        for child_genome_property_id in evidence.genome_property_identifiers:

                            if child_genome_property_id in genome_property_assignments:
                                current_step_result = genome_property_assignments[child_genome_property_id]
                                functional_element_results.append(current_step_result)
                            else:
                                child_genome_property_result, \
                                genome_property_assignments, \
                                global_step_assignments = assign_genome_properties(genome_properties_tree,
                                                                                   genome_property_assignments,
                                                                                   global_step_assignments,
                                                                                   child_genome_property_id)

                                functional_element_results.append(child_genome_property_result)
                if 'NO' in functional_element_results:
                    current_step_result = False
                else:
                    current_step_result = True

        current_step_assignments[step_number] = current_step_result

    current_step_assignment_values = list(current_step_assignments.values())
    true_count = current_step_assignment_values.count(True)

    if true_count == len(current_step_assignment_values):
        genome_property_result = 'YES'
    elif true_count > current_genome_property.threshold:
        genome_property_result = 'PARTIAL'
    else:
        genome_property_result = 'NO'

    global_step_assignments[genome_property_id] = current_step_assignments
    genome_property_assignments[genome_property_id] = genome_property_result

    return genome_property_result, genome_property_assignments, global_step_assignments
