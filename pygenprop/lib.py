#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: A set of helper functions.
"""

from os import path


def sanitize_cli_path(cli_path):
    """
    Performs expansion of '~' and shell variables such as "$HOME" into absolute paths.

    :param cli_path: The path to expand
    :return: An expanded path.
    """
    sanitized_path = path.expanduser(path.expandvars(cli_path))
    return sanitized_path
