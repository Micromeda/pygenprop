#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2018)

Description: The genome property tree class.
"""

import json

import pandas as pd
from skbio.sequence import Protein
from sqlalchemy import engine as SQLAlchemyEngine
from sqlalchemy.orm import sessionmaker

from pygenprop.assign import AssignmentCache, AssignmentCacheWithMatches
from pygenprop.assignment_database import Base, Sample, PropertyAssignment, StepAssignment
from pygenprop.tree import GenomePropertiesTree


class GenomePropertiesResults(object):
    """
    This class contains a representation of a table of results from one or more genome properties assignments.
    """

    def __init__(self, *genome_properties_results: AssignmentCache, properties_tree: GenomePropertiesTree):
        """
        Constructs the genome properties results object.

        :param properties_tree: The global genome properties tree.
        :param genome_properties_results: One or more parsed genome properties assignments.
        """

        property_tables = []
        step_tables = []
        sample_names = []
        for assignment in genome_properties_results:
            sample_names.append(assignment.sample_name)
            property_table, step_table = assignment.create_results_tables(properties_tree)
            property_tables.append(property_table)
            step_tables.append(step_table)

        combined_properties_table = pd.concat(property_tables, axis=1)
        combined_step_table = pd.concat(step_tables, axis=1)
        combined_properties_table.columns = sample_names
        combined_step_table.columns = sample_names

        self._sample_names = None
        self.tree = properties_tree
        self.property_results = combined_properties_table.sort_index()
        self.step_results = combined_step_table.sort_index()
        self.sample_names = sample_names

    @property
    def sample_names(self):
        """
        Returns the sample names for samples represented by the results objects.

        :return: The current sample names
        """
        return self._sample_names

    @sample_names.setter
    def sample_names(self, new_sample_names: list):
        """
        Replaces the current sample names with new sample names.

        :param new_sample_names: A list containing the new sample names
        """
        self._sample_names = new_sample_names
        old_sample_names = self.property_results.columns.tolist()
        old_to_new_mapping = dict(zip(old_sample_names, new_sample_names))
        self.property_results.rename(columns=old_to_new_mapping, inplace=True)
        self.step_results.rename(columns=old_to_new_mapping, inplace=True)

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

    @property
    def properties(self):
        """
        Generates a list of properties for which there are assignments for.
        :return: A list of genome property identifiers.
        """
        return self.property_results.index.tolist()

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
            summary = results.apply(pd.value_counts, normalize=normalize).fillna(0) * 100
        else:
            summary = results.apply(pd.value_counts, normalize=normalize).fillna(0)

        return summary

    def get_property_result(self, genome_property_id, sample=None):
        """
        Gets the assignment results for a given genome property.

        :param sample: The sample for which to grab results for.
        :param genome_property_id: The id of the genome property to get results for.
        :return: A list containing the assignment results for the genome property in question.
        """

        if sample:
            property_results = self.property_results[sample]
        else:
            property_results = self.property_results

        try:
            if sample:
                property_result = property_results.loc[genome_property_id]
            else:
                property_result = property_results.loc[genome_property_id].tolist()
        except KeyError:
            property_result = ['NO'] * len(property_results.columns)

        return property_result

    def get_step_result(self, genome_property_id, step_number, sample=None):
        """
        Gets the assignment results for a given step of a genome property.

        :param sample: The sample for which to grab results for.
        :param genome_property_id: The id of the genome property that the step belongs too.
        :param step_number: The step number of the step.
        :return: A list containing the assignment results for the step in question.
        """

        if sample:
            step_results = self.step_results[sample]
        else:
            step_results = self.step_results

        try:
            if sample:
                property_result = step_results.loc[genome_property_id].loc[step_number]
            else:
                property_result = step_results.loc[genome_property_id].loc[step_number].tolist()
        except KeyError:
            property_result = ['NO'] * len(step_results.columns)
        return property_result

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

    def get_step_numbers_for_property(self, genome_property_id):
        """
        Gets the numbers of the steps that support a property.
        :param genome_property_id: The id of the genome property for which we wants steps.
        :return: A list of step numbers.
        """
        return self.step_results.loc[genome_property_id].index.tolist()

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

    def to_assignment_database(self, engine: SQLAlchemyEngine):
        """
        Write the given results object to an SQL database.

        :param engine: An SQLAlchemyEngine connection object.
        """

        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        current_session = sessionmaker(bind=engine)()
        for sample_name in self.sample_names:
            sample = Sample(name=sample_name)

            sample_step_assignments = []
            sample_property_assignments = []
            for property_identifier in self.properties:
                property_result = self.get_property_result(property_identifier,
                                                           sample=sample.name)

                property_assignment = PropertyAssignment(sample=sample)
                property_assignment.identifier = property_identifier
                property_assignment.assignment = property_result

                current_steps_assignments = []
                for step_number in self.get_step_numbers_for_property(property_identifier):
                    step_result = self.get_step_result(property_identifier, step_number, sample=sample.name)

                    if step_result == 'YES':
                        current_steps_assignments.append(StepAssignment(number=step_number,
                                                                        property_assignment=property_assignment))
                    else:
                        continue  # Skip steps which are not 'YES' to save space.

                property_assignment.step_assignments = current_steps_assignments
                sample_step_assignments.extend(current_steps_assignments)
                sample_property_assignments.append(property_assignment)

            current_session.add_all([sample, *sample_property_assignments, *sample_step_assignments])
        current_session.commit()
        current_session.close()


def load_assignment_caches_from_database(engine):
    """
    Creates a series of assignment caches from an assignment database file.

    :param engine: An SQLAlchemy engine
    :return: List of assignment caches representing the assignments stored in the database.
    """
    current_session = sessionmaker(bind=engine)()
    assignment_caches = []
    for sample in current_session.query(Sample):
        sample_cache = AssignmentCache(sample_name=sample.name)
        for property_assignment in sample.property_assignments:
            sample_cache.cache_property_assignment(property_assignment.identifier, property_assignment.assignment)
            for step_assignment in property_assignment.step_assignments:
                sample_cache.cache_step_assignment(property_assignment.identifier, step_assignment.number,
                                                   step_assignment.assignment)
        assignment_caches.append(sample_cache)
    return assignment_caches


class GenomePropertiesResultsWithMatches(GenomePropertiesResults):
    """
    This class extends the GenomePropertiesResults object to include supporting information such as InterProScan
    E-values and FASTA sequences of proteins that support property existence.
    """

    def __init__(self, *genome_properties_results: AssignmentCacheWithMatches, properties_tree: GenomePropertiesTree):
        """
        Constructs the extended genome properties results object.

        :param genome_properties_results: One or more parsed genome properties assignments.
        :param properties_tree: The global genome properties tree.
        """

        GenomePropertiesResults.__init__(*genome_properties_results, properties_tree=properties_tree)
        property_identifiers = properties_tree.consortium_identifiers_dataframe

        all_matches = []
        for assignment in genome_properties_results:
            step_matches = property_identifiers.merge(assignment.matches, left_on='Signature_Accession',
                                                      right_index=True, copy=False)

            # Drop genome properties which are not found in the assignment cache.
            step_matches.drop(assignment.get_unshared_identifiers(properties_tree),
                              axis=0, level=0, errors='ignore', inplace=True)

            all_matches.append(pd.concat([step_matches], keys=[assignment.sample_name], names=['Sample_Name']))

        self.step_matches = pd.concat(all_matches, copy=False).sort_index()

    @property
    def top_step_matches(self):
        """
        Filters matches to those with the lowest E-values.

        :return: A step matches dataframe
        """
        return self.step_matches.sort_values('E-value').groupby(['Sample_Name',
                                                                 'Property_Identifier',
                                                                 'Step_Number'])['Signature_Accession',
                                                                                 'Protein_Accession',
                                                                                 'E-value', 'Sequence'].first()

    def get_property_matches(self, genome_property_id, sample=None, top=False):
        """
        Gets the assignment results for a given genome property.

        :param top: Get only the matches with the lowest e-value.
        :param sample: The sample for which to grab results for.
        :param genome_property_id: The id of the genome property to get results for.
        :return: A list containing the assignment results for the genome property in question.
        """

        if top:
            all_matches = self.top_step_matches
        else:
            all_matches = self.step_matches

        if sample:
            matches = all_matches.loc[sample].loc[genome_property_id]
        else:
            matches = all_matches.reorder_levels(['Property_Identifier', 'Step_Number',
                                                  'Sample_Name']).loc[genome_property_id]

        return matches

    def get_step_matches(self, genome_property_id, step_number, sample=None, top=False):
        """
        Gets the assignment results for a given step of a genome property.

        :param top: Get only the matches with the lowest e-value.
        :param sample: The sample for which to grab results for.
        :param genome_property_id: The id of the genome property that the step belongs too.
        :param step_number: The step number of the step.
        :return: A list containing the assignment results for the step in question.
        """

        property_matches = self.get_property_matches(genome_property_id, sample=sample, top=top)
        return property_matches.loc[step_number]

    def get_proteins_for_matches(self, genome_property_id, step_number, top=False):
        """
        Creates a series of protein objects representing the proteins which support specific genome property steps.

        :param genome_property_id: The id of the genome property that the step belongs too.
        :param step_number: The step number of the step.
        :param top: Get only the matches with the lowest e-value.
        :return: A list of protein sequence objects
        """
        step_sequences = self.get_step_matches(genome_property_id, step_number,
                                               top=top)[['Protein_Accession', 'Sequence']]

        return step_sequences.apply(self.create_protein_sequence, axis=1).tolist()

    @staticmethod
    def create_protein_sequence(matches_row):
        """
        Creates a protein object from a row of a step matches dataframe.

        :param matches_row: A dataframe row from a step matches dataframe
        :return: A protien object
        """
        return Protein(sequence=(matches_row['Sequence']), metadata={'id': (matches_row['Protein_Accession'])})

    def write_matches_fasta(self, file_handle, genome_property_id, step_number, top=False):
        """
        Write proteins which cause InterProScan matches for a genome property step to FASTA file.

        :param file_handle: A file handle object to write the file to.
        :param genome_property_id: The id of the genome property that the step belongs too.
        :param step_number: The step number of the step.
        :param top: Get only the matches with the lowest e-value.
        """
        match_sequences = self.get_proteins_for_matches(genome_property_id, step_number, top=top)

        for sequence in match_sequences:
            sequence.write(file_handle, format='fasta')
