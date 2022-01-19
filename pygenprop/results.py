#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2018)

Description: The genome property tree class.
"""

import json
from collections import defaultdict
from functools import partial
from math import isnan

import pandas as pd
import pickle
from skbio.sequence import Protein
from sqlalchemy import engine as SQLAlchemyEngine
from sqlalchemy.orm import sessionmaker

from pygenprop.assign import AssignmentCache, AssignmentCacheWithMatches
from pygenprop.assignment_database import Base, Sample, PropertyAssignment, StepAssignment, InterProScanMatch, \
    Sequence, step_match_association_table
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
        Display counts or percentage of yes no partial assignment for the given properties or steps of the given
        properties.

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

    def to_assignment_database(self, engine: SQLAlchemyEngine, drop_existing=True):
        """
        Write the given results object to an SQL database.

        :param drop_existing: Drop all existing tables in the database before insert.
        :param engine: An SQLAlchemyEngine connection object.
        """

        if drop_existing:
            Base.metadata.drop_all(engine)

        Base.metadata.create_all(engine, checkfirst=True)
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

    def to_serialization(self):
        """
        Creates a serialization of the results object.

        :return: A msgpack format serialization of the results object.
        """
        results_frames = (self.property_results,
                          self.step_results)
        return pickle.dumps(results_frames)


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
        load_sample_assignments_from_database(sample_cache, sample)
        assignment_caches.append(sample_cache)

    current_session.close()

    return assignment_caches


def load_sample_assignments_from_database(sample_cache, sample):
    """
    For a given sample, loads the sample property and step assignments from the database.

    :param sample_cache: A sample cache to put property and step assignments into.
    :param sample: A Sample object (SQLAlchemy table class)
    """
    for property_assignment in sample.property_assignments:
        sample_cache.cache_property_assignment(property_assignment.identifier, property_assignment.assignment)
        for step_assignment in property_assignment.step_assignments:
            sample_cache.cache_step_assignment(property_assignment.identifier, step_assignment.number,
                                               step_assignment.assignment)


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

        GenomePropertiesResults.__init__(self, *genome_properties_results, properties_tree=properties_tree)
        property_identifiers = properties_tree.consortium_identifiers_dataframe

        all_matches = []
        for assignment in genome_properties_results:
            step_matches = property_identifiers.merge(assignment.matches, left_on='Signature_Accession',
                                                      right_index=True, copy=False)

            # Drop genome properties which are not found in the assignment cache.
            step_matches.drop(assignment.get_unshared_identifiers(properties_tree),
                              axis=0, level=0, errors='ignore', inplace=True)

            all_matches.append(pd.concat([step_matches], keys=[assignment.sample_name], names=['Sample_Name']))

        # Vertically join all matches from all samples into a single table.
        step_matches = pd.concat(all_matches, copy=False)

        # Keep matches for ony steps which are assigned "YES". Drop those which are found for "NO" assignments.
        # Note: Unfortunately, this drops matches for step assignments which were assigned NO due to partial evidence.
        # For example, the step has evidence from one InterPro sig. but not the other which is also required. We decided
        # to drop IPR5 matches for these partial assignments in order to save space in micromeda files and to simplify
        # our ability to determine if our micromeda files are saving correctly. We assume finding IPR5 matches for
        # assignments assigned NO is a corner case.

        # Converted supported steps to dataframe whose index can be used as a filter.
        supported_steps = self.supported_step_results.stack()

        if isinstance(supported_steps, pd.Series):
            supported_steps = supported_steps.to_frame()

        supported_steps.index.rename('Sample_Name', level=2, inplace=True)
        supported_steps = supported_steps.reorder_levels(['Sample_Name', 'Property_Identifier', 'Step_Number'])

        # Filter to only supported ('YES') steps.
        supported_step_matches = step_matches[step_matches.index.isin(supported_steps.index)]

        self.step_matches = supported_step_matches.sort_index()

    def get_sample_matches(self, sample, top=False):
        """
        Get matches for a single sample.

        :param sample: The sample for which to grab results for.
        :param top: Get only the matches with the lowest e-value.
        :return:
        """
        if top:
            all_matches = self._top_step_matches
        else:
            all_matches = self.step_matches

        try:
            sample_matches = all_matches.loc[sample]
        except KeyError:
            sample_matches = None

        return sample_matches

    def get_property_matches(self, genome_property_id, sample=None, top=False):
        """
        Gets the assignment results for a given genome property.

        :param top: Get only the matches with the lowest e-value.
        :param sample: The sample for which to grab results for.
        :param genome_property_id: The id of the genome property to get results for.
        :return: A list containing the assignment results for the genome property in question.
        """

        if top:
            all_matches = self._top_step_matches
        else:
            all_matches = self.step_matches

        try:
            if sample:
                matches = all_matches.loc[sample].loc[genome_property_id]
            else:
                matches = all_matches.reorder_levels(['Property_Identifier', 'Step_Number',
                                                      'Sample_Name']).loc[genome_property_id]
                matches = matches.reorder_levels(['Sample_Name', 'Step_Number'])
        except KeyError:
            matches = None

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

        try:
            property_matches = self.get_property_matches(genome_property_id, sample=sample, top=top)
            if property_matches is not None:
                if isinstance(property_matches.index, pd.MultiIndex):
                    property_matches = property_matches.reorder_levels(['Step_Number', 'Sample_Name'])

                step_matches = property_matches.loc[step_number]
            else:
                step_matches = None
        except KeyError:
            step_matches = None

        return step_matches

    def get_supporting_proteins_for_step(self, genome_property_id, step_number, top=False):
        """
        Creates a series of protein objects representing the proteins which support specific genome property steps.

        :param genome_property_id: The id of the genome property that the step belongs too.
        :param step_number: The step number of the step.
        :param top: Get only the matches with the lowest e-value.
        :return: A list of skbio protein sequence objects
        """
        step_matches = self.get_step_matches(genome_property_id, step_number, top=top)

        if step_matches is not None:
            step_sequences = step_matches.reset_index()[['Sample_Name', 'Protein_Accession', 'Sequence']]
            proteins = step_sequences.apply(self.create_skbio_protein_sequence, axis=1).tolist()
        else:
            proteins = None
        return proteins

    def write_supporting_proteins_for_step_fasta(self, file_handle, genome_property_id, step_number, top=False):
        """
        Write proteins which cause InterProScan matches for a genome property step to FASTA file.

        :param file_handle: A file handle object to write the file to.
        :param genome_property_id: The id of the genome property that the step belongs too.
        :param step_number: The step number of the step.
        :param top: Get only the matches with the lowest e-value.
        """
        match_sequences = self.get_supporting_proteins_for_step(genome_property_id, step_number, top=top)

        if match_sequences is not None:
            for sequence in match_sequences:
                sequence.write(file_handle, format='fasta')
        else:
            raise KeyError

    def to_assignment_database(self, engine: SQLAlchemyEngine, drop_existing=True):
        """
        Write the given results object to an SQL database.

        :param drop_existing: Drop all existing tables in the database before insert.
        :param engine: An SQLAlchemyEngine connection object.
        """

        if drop_existing:
            Base.metadata.drop_all(engine)

        Base.metadata.create_all(engine, checkfirst=True)
        current_session = sessionmaker(bind=engine)()

        # Write samples, genome property assignments and step assignments to the database.
        GenomePropertiesResults.to_assignment_database(self, engine=engine, drop_existing=False)

        for sample in current_session.query(Sample):

            unique_interproscan = self._get_unique_interproscan_matches(sample.name).apply(
                self.create_interproscan_match,
                axis=1).tolist()
            unique_sequences = self._get_unique_sequences(sample.name).apply(self.create_sequence, axis=1).tolist()

            current_session.add_all([*unique_interproscan, *unique_sequences])

            unique_sequence_dict = {sequence.identifier: sequence for sequence in unique_sequences}

            unique_interproscan_dict = defaultdict(lambda: defaultdict(dict))
            for interproscan in unique_interproscan:
                # Add matching sequences as children of interproascan matches
                interproscan.sequence = unique_sequence_dict[interproscan.sequence_identifier]

                # Add interproscan object to the interproscan match dict.
                unique_interproscan_dict[interproscan.interpro_signature][interproscan.sequence_identifier][
                    interproscan.expected_value] = interproscan

            for property_assignment in sample.property_assignments:
                for step_assignment in property_assignment.step_assignments:
                    step_matches = self.get_step_matches(property_assignment.identifier, step_assignment.number,
                                                         sample=sample.name)

                    if step_matches is not None:
                        wrapper = partial(self.connect_step_assignments_to_interproscan_matches,
                                          step_assignment=step_assignment,
                                          unique_interproscan_dict=unique_interproscan_dict)

                        # Add the interproscan matches to each step assignment
                        if isinstance(step_matches, pd.Series):
                            wrapper(step_matches)
                        else:
                            step_matches.apply(wrapper, axis=1)

        current_session.commit()
        current_session.close()

    @property
    def _top_step_matches(self):
        """
        Filters matches to those with the lowest E-values.

        :return: A step matches dataframe
        """
        return self.step_matches.sort_values('E-value').groupby(['Sample_Name',
                                                                 'Property_Identifier',
                                                                 'Step_Number'])[['Signature_Accession',
                                                                                  'Protein_Accession',
                                                                                  'E-value', 'Sequence']].first()

    def _get_unique_matches(self, sample=None, top=False, sequences=False):
        """
        If a protein contains multiple copies of the exact same domain, only return one copy.
        Get unique matches for a sample or across all samples in the dataset.

        :param sample: The sample for which to grab results for.
        :param top: Get only the matches with the lowest e-value.
        :param sequences: Retrieve only unique protein sequences
        :return: A dataframe of unique matches
        """
        if top:
            all_matches = self._top_step_matches
        else:
            all_matches = self.step_matches

        if sample:
            all_matches = all_matches.loc[sample]

        if sequences:
            result = all_matches.reset_index()[['Protein_Accession', 'Sequence']].drop_duplicates()
        else:
            result = all_matches.reset_index()[['Signature_Accession', 'Protein_Accession',
                                                'E-value']].drop_duplicates()
        return result

    def _get_unique_interproscan_matches(self, sample=None, top=False):
        """
        Get unique interproscan matches for a sample or across all samples in the dataset.

        :param sample: The sample for which to grab results for.
        :param top: Get only the matches with the lowest e-value.
        :return: A dataframe of unique inteproscan matches
        """
        return self._get_unique_matches(sample=sample, top=top)

    def _get_unique_sequences(self, sample=None, top=False):
        """
        Get unique sequences for a sample or across all samples in the dataset.

        :param sample: The sample for which to grab results for.
        :param top: Get only the matches with the lowest e-value.
        :return: A dataframe of unique sequences
        """
        return self._get_unique_matches(sample=sample, top=top, sequences=True)

    @staticmethod
    def create_skbio_protein_sequence(match_row):
        """
        Creates a protein object from a row of a step matches dataframe.

        :param match_row: A dataframe row from a step matches dataframe
        :return: A protein object
        """
        metadata = {'id': match_row['Protein_Accession'], 'description': ('(From ' + match_row['Sample_Name'] + ')')}
        return Protein(sequence=match_row['Sequence'], metadata=metadata)

    @staticmethod
    def create_interproscan_match(match_row):
        """
        Creates a assignment database InterProScanMatch object from a row of a step matches dataframe.

        :param match_row: A dataframe row from a step matches dataframe
        :return: An assignment database InterProScanMatch sqlalchemy object
        """

        return InterProScanMatch(sequence_identifier=match_row['Protein_Accession'],
                                 interpro_signature=match_row['Signature_Accession'],
                                 expected_value=match_row['E-value'])

    @staticmethod
    def create_sequence(match_row):
        """
        Creates a assignment database InterProScanMatch object from a row of a step matches dataframe.

        :param match_row: A dataframe row from a step matches dataframe
        :return: An assignment database InterProScanMatch sqlalchemy object
        """
        return Sequence(identifier=match_row['Protein_Accession'], sequence=match_row['Sequence'])

    @staticmethod
    def connect_step_assignments_to_interproscan_matches(match_row, step_assignment, unique_interproscan_dict):
        """
        Connects each step assigment object to its child interproscan objects.

        :param match_row: A dataframe row from a step matches dataframe
        :param step_assignment: A step assignment object that is parent to the matches.
        :param unique_interproscan_dict: A dict of unique interproscan objects indexed by a triple level dict.
        """
        interpro_signature = match_row['Signature_Accession']
        protein_identifier = match_row['Protein_Accession']
        e_value = match_row['E-value']

        matches_for_protein = unique_interproscan_dict[interpro_signature][protein_identifier]
        try:
            current_interproscan = matches_for_protein[e_value]
        except KeyError:
            '''
            Two independently generated nan values are not equal as they are both objects. In cases where the e-value of
            a protein match is left blank the resulting InterProScanMatch object object's e-value is set to NaN. The 
            code above selects a InterProScanMatch object from a dict of dict of dict. The inner most 
            layer of this data structure is a index by e-value. However, the NaN object of the e_value of the match row
            is not the same as the NaN object found in the keys the inner layer of the dict of dict of dict. Thus a key 
            error is returned even though both values are NaN. This except block checks if the missing value is 
            NaN and if so it the block automatically returns the appropriate InterProScanMatch object.
            '''

            nan_matches = [match for e_value, match in matches_for_protein.items() if isnan(e_value)]
            if len(nan_matches) > 0:
                current_interproscan = nan_matches[0]
            else:
                raise KeyError

        step_assignment.interproscan_matches.append(current_interproscan)

    def to_serialization(self):
        """
        Creates a serialization of the results object.

        :return: A msgpack format serialization of the results object.
        """
        results_frames = (self.property_results,
                          self.step_results,
                          self.step_matches)
        return pickle.dumps(results_frames)


def load_assignment_caches_from_database_with_matches(engine):
    """
    Creates a series of assignment caches from an assignment database file.

    :param engine: An SQLAlchemy engine
    :return: List of assignment caches representing the assignments stored in the database.
    """
    current_session = sessionmaker(bind=engine)()

    assignment_caches = []
    for sample in current_session.query(Sample):
        query_part_one = current_session.query(InterProScanMatch.interpro_signature,
                                               InterProScanMatch.sequence_identifier,
                                               InterProScanMatch.expected_value,
                                               Sequence.sequence)

        query_part_two = query_part_one.join(Sequence).join(step_match_association_table)
        query_part_three = query_part_two.join(StepAssignment).join(PropertyAssignment).join(Sample)
        final_query = query_part_three.filter(Sample.name == sample.name).distinct()

        matches_frame = pd.read_sql(final_query.statement, engine)
        matches_frame.columns = ['Signature_Accession', 'Protein_Accession', 'E-value', 'Sequence']
        matches_frame.set_index('Signature_Accession', inplace=True)

        sample_cache = AssignmentCacheWithMatches(sample_name=sample.name)
        sample_cache.matches = matches_frame

        load_sample_assignments_from_database(sample_cache, sample)

        assignment_caches.append(sample_cache)

    current_session.close()

    return assignment_caches


class GenomePropertiesResultsFromDataFrames(GenomePropertiesResultsWithMatches):
    """
    A mock class that build an object analogous to a GenomePropertiesResultsWithMatches object but built from
    DataFrames. This is useful for building GenomePropertiesResultsWithMatches with matches objects from copies
    of their underlying results DataFrames.
    """

    def __init__(self, property_results_frame, step_results_frame, properties_tree, step_matches_frame=None):
        """
        Constructs the GenomePropertiesResultsWithMatchesFromDataFrames object.

        :param property_results_frame: A GenomePropertiesResultsWithMatches property_results DataFrame.
        :param step_results_frame: A GenomePropertiesResultsWithMatches step_results DataFrame.
        :param step_matches_frame: A GenomePropertiesResultsWithMatches step_matches DataFrame.
        :param properties_tree: The global genome properties tree.
        """
        self.property_results = property_results_frame
        self.step_results = step_results_frame
        self.step_matches = step_matches_frame
        self.tree = properties_tree
        self.sample_names = self.property_results.columns.tolist()


def load_results_from_serialization(serialized_results, properties_tree: GenomePropertiesTree):
    """
    Takes a msgpack serialization and converts it to a GenomePropertiesResults object.

    :param serialized_results: Results in msgpack format.
    :param properties_tree: The global genome properties tree.
    :return: Either a GenomePropertiesResultsWithMatches or a GenomePropertiesResults.
    """
    stored_dataframes = pickle.loads(serialized_results)
    property_results = stored_dataframes[0]
    step_results = stored_dataframes[1]

    result = GenomePropertiesResultsFromDataFrames(property_results_frame=property_results,
                                                   step_results_frame=step_results,
                                                   properties_tree=properties_tree)
    if len(stored_dataframes) > 2:
        result.step_matches = stored_dataframes[2]
        result.__class__ = GenomePropertiesResultsWithMatches
    else:
        result.__class__ = GenomePropertiesResults

    return result
