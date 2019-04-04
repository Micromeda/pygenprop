#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2018)

Description: The genome property tree class.
"""

import json
import pandas as pd

from pygenprop.assign import assign_genome_property, AssignmentCache
from pygenprop.tree import GenomePropertiesTree
from copy import deepcopy


class GenomePropertiesResults(object):
    """
    This class contains a representation of a table of results from one or more genome properties assignments.
    """

    def __init__(self, *genome_properties_results: AssignmentCache, properties_tree: GenomePropertiesTree):
        """
        Constructs the genome properties results object.

        :param properties_tree: The global genome properties tree.
        :param genome_properties_results_dict: One or more parsed genome properties assignments.
        """

        property_tables = []
        step_tables = []
        sample_names = []
        for assignment in genome_properties_results:
            sample_names.append(assignment.sample_name)
            property_table, step_table = create_assignment_tables(properties_tree, assignment)
            property_tables.append(property_table)
            step_tables.append(step_table)

        combined_properties_table = pd.concat(property_tables, axis=1)
        combined_step_table = pd.concat(step_tables, axis=1)
        combined_properties_table.columns = sample_names
        combined_step_table.columns = sample_names

        self.tree = properties_tree
        self.sample_names = sample_names
        self.property_results = combined_properties_table
        self.step_results = combined_step_table

    def get_results(self, *property_identifiers, steps=False, names=False):
        """
        Creates a results dataframe for only a subset of genome properties.

        :param property_identifiers: The id of one or more genome properties to get results for.
        :param steps: Add steps to the dataframe.
        :param names: Add property and or step names to the dataframe.
        :return: A dataframe with results for a specific set of genome properties.
        """
        if steps:
            results = self.step_results
        else:
            results = self.property_results

        filtered_results = results.loc[results.index.get_level_values(0).isin(property_identifiers)]

        if names:
            named_results = filtered_results.reset_index()

            named_results['Property_Name'] = named_results['Property_Identifier'].apply(
                lambda property_identifier: self.tree[property_identifier].name)

            if steps:
                named_results['Step_Name'] = named_results[['Property_Identifier', 'Step_Number']].apply(
                    lambda row: self.get_step_name(row['Property_Identifier'], row['Step_Number']), axis=1)

                filtered_results = named_results.set_index(['Property_Identifier', 'Property_Name',
                                                            'Step_Number', 'Step_Name'])
            else:
                filtered_results = named_results.set_index(['Property_Identifier', 'Property_Name'])

        return filtered_results

    def get_step_name(self, property_identifier, step_number):
        """
        Helper function to quickly acquire a property steps name.

        :param property_identifier: The id of the genome property.
        :param step_number: The step number of the step.
        :return: The steps name.
        """
        genome_property = self.tree[property_identifier]
        step_name = 'None'
        for step in genome_property.steps:
            if step.number == step_number:
                step_name = step.name
                break
        return step_name

    def get_results_summary(self, *property_identifiers, steps=False, normalize=False):
        """
        Creates a summary table for yes, no and partial assignments of a given set of properties or property steps.
        Display counts or percentage of yes no partial assignment for the given properties or steps of the given properties.

        :param property_identifiers: The id of one or more genome properties to get results for.
        :param steps: Summarize results for the steps of the input properties
        :param normalize: Display the summary as a percent rather than as counts.
        :return: A summary table dataframe
        """
        results = self.get_results(*property_identifiers, steps=steps)

        if normalize:
            summary = results.apply(pd.value_counts, normalize=normalize).fillna(0)*100
        else:
            summary = results.apply(pd.value_counts, normalize=normalize).fillna(0)

        return summary

    def get_property_result(self, genome_property_id):
        """
        Gets the assignment results for a given genome property.

        :param genome_property_id: The id of the genome property to get results for.
        :return: A list containing the assignment results for the genome property in question.
        """
        property_results = self.property_results

        try:
            property_result = property_results.loc[genome_property_id].tolist()
        except KeyError:
            property_result = ['NO'] * len(property_results.columns)

        return property_result

    def get_step_result(self, genome_property_id, step_number):
        """
        Gets the assignment results for a given step of a genome property.

        :param genome_property_id: The id of the genome property that the step belongs too.
        :param step_number: The step number of the step.
        :return: A list containing the assignment results for the step in question.
        """
        step_results = self.step_results

        try:
            property_result = step_results.loc[genome_property_id].loc[step_number].tolist()
        except KeyError:
            property_result = ['NO'] * len(step_results.columns)
        return property_result

    @property
    def differing_property_results(self):
        """
        Property results where all properties differ in assignment in at least one sample.
        :return: A property result data frame where properties with the all the same value are filtered out.
        """
        return self.remove_results_with_shared_assignments(self.property_results)

    @property
    def differing_step_results(self):
        """
        Step results where all steps differ in assignment in at least one sample.
        :return: A step result data frame where properties with the all the same value are filtered out.
        """
        return self.remove_results_with_shared_assignments(self.step_results)

    @property
    def supported_property_results(self):
        """
        Property results where properties which are not supported in any sample are removed.
        :return: A property result data frame where properties with the all NO values are filtered out.
        """
        return self.remove_results_with_shared_assignments(self.property_results, only_drop_no_assignments=True)

    @property
    def supported_step_results(self):
        """
        Step results where steps which are not supported in any sample are removed.
        :return: A step result data frame where steps with the all NO values are filtered out.
        """
        return self.remove_results_with_shared_assignments(self.step_results, only_drop_no_assignments=True)

    @staticmethod
    def remove_results_with_shared_assignments(results, only_drop_no_assignments=False):
        """
        Filter out results where all samples have the same value.
        :param results: A step or property results data frame.
        :param only_drop_no_assignments: Only drop results where values are all NO.
        :return: A step or property data frame with certain properties filtered out.
        """
        results_transposed = results.transpose()
        number_of_unique_values_per_column = results_transposed.apply(pd.Series.nunique)
        single_value_columns = number_of_unique_values_per_column[number_of_unique_values_per_column == 1].index

        if only_drop_no_assignments:
            results_to_drop = \
                [column for column in single_value_columns if results_transposed[column].unique()[0] == 'NO']
        else:
            results_to_drop = [column for column in single_value_columns]  # Drop all single value columns.

        return results_transposed.drop(results_to_drop, axis=1).transpose()

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


def create_assignment_tables(genome_properties_tree: GenomePropertiesTree, assignment_cache: AssignmentCache):
    """
    Takes a results dictionary from the long form parser and creates two tables. One for property results and
    one for step results. The longform results file has only leaf assignment results. We have to bootstrap the rest.

    :param genome_properties_tree: The global genome properties tree.
    :param assignment_cache: Per-sample genome properties results from the long form parser.
    :return: A tuple containing an property assignment table and step assignments table.
    """
    sanitized_assignment_cache = create_synchronized_assignment_cache(assignment_cache, genome_properties_tree)

    # Take known assignments and matched InterPro member database
    # identifiers and calculate assignments for all properties.
    assignments = bootstrap_assignments(sanitized_assignment_cache, genome_properties_tree)

    property_table = pd.DataFrame.from_dict(assignments.property_assignments,
                                            orient='index', columns=['Property_Result'])
    property_table.index.names = ['Property_Identifier']

    step_table = pd.DataFrame(create_step_table_rows(assignments.step_assignments),
                              columns=['Property_Identifier', 'Step_Number', 'Step_Result'])
    step_table.set_index(['Property_Identifier', 'Step_Number'], inplace=True)

    return property_table, step_table


def bootstrap_assignments(assignment_cache, genome_properties_tree):
    """
    Recursively fills in assignments for all genome properties in the genome properties tree based of existing cached
    assignments and InterPro member database identifiers.

    :param assignment_cache: A cache containing step and property assignments and InterPro member database matches.
    :param genome_properties_tree:
    :return:
    """
    # Bootstrap the other assignments from the leaf assignments.
    assign_genome_property(assignment_cache, genome_properties_tree.root)

    return assignment_cache


def create_synchronized_assignment_cache(assignment_cache, genome_properties_tree):
    """
    Remove genome properties from the assignment cache that are not found in both the genome properties tree and
    the assignment cache. This prevents situations where different versions of the cache and tree cannot find each
    others genome properties.

    :param assignment_cache: A cache containing step and property assignments and InterPro member database matches.
    :param genome_properties_tree: The global genome properties tree.
    :return: An assignment cache containing data for genome properties shared between the tree and cache.
    """
    tree_identifiers = genome_properties_tree.genome_property_identifiers
    assignment_cache_identifiers = set(assignment_cache.genome_property_identifiers)

    unshared_identifiers = tree_identifiers.symmetric_difference(assignment_cache_identifiers)

    sanitized_assignment_cache = deepcopy(assignment_cache)

    for identifier in unshared_identifiers:
        sanitized_assignment_cache.flush_property_from_cache(identifier)

    return sanitized_assignment_cache


def create_step_table_rows(step_assignments):
    """
    Unfolds a step result dict of dict and yields a step table row.

    :param step_assignments: A dict of dicts containing step assignment information ({gp_key -> {stp_key --> result}})
    """
    for genome_property_id, step in step_assignments.items():
        for step_number, step_result in step.items():
            yield genome_property_id, step_number, step_result
