#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2018)

Description: The genome property tree class.
"""

from modules.genome_properties_tree import GenomePropertiesTree
import pandas as pd
import json


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
