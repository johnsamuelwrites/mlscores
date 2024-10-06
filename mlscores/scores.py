#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

def calculate_language_percentage(properties, language):
    """
    Calculate the percentage of properties in the given language.

    This function takes a list of properties and a target language, and returns the percentage
    of properties that are in the target language.

    Args:
        properties (list): A list of tuples containing property information, where each tuple
            contains the property, its value, and its language.
        language (str): The target language to calculate the percentage for.

    Returns:
        float: The percentage of properties in the target language, or 0 if there are no properties.

    Notes:
        This function uses a set to store unique properties and a dictionary to store the count
        of properties for each language.
    """
    # Use a set to store unique properties
    unique_properties = set(prop for prop, _, _ in properties)

    # Use a dictionary to store the count of properties for each language
    language_count = {}
    for i, (prop, _, lang) in enumerate(properties):
        if lang not in language_count:
            language_count[lang] = set()
        language_count[lang].add(prop)

    # Calculate the percentage of properties in the given language
    if not unique_properties:
        return 0

    language_percentage = (
        len(language_count.get(language, set())) / len(unique_properties)
    ) * 100

    return language_percentage
