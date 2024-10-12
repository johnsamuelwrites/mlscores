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


def calculate_language_percentage_for_languages(properties, languages):
    """
    Calculate the percentage of properties for each language.

    This function takes a list of properties with their corresponding languages and a list of languages,
    and returns a dictionary where the keys are the languages and the values are the percentages of properties for each language.

    Args:
        properties (list): A list of tuples containing the property, its value, and its language.
        languages (list): A list of languages to calculate the percentages for.

    Returns:
        A dictionary where the keys are the languages and the values are the percentages of properties for each language.

    Notes:
        This function uses a set to store unique properties and a dictionary to store the count of properties for each language.
    """
    # Use a set to store unique properties
    unique_properties = set(prop for prop, _, _ in properties)

    # Use a dictionary to store the count of properties for each language
    language_count = {}
    for prop, _, lang in properties:
        if lang not in language_count:
            language_count[lang] = set()
        language_count[lang].add(prop)

    # Calculate the percentage of properties for each language
    language_percentages = {}
    for lang in languages:
        if not unique_properties:
            # If there are no unique properties, set the percentage to 0
            language_percentages[lang] = 0
        else:
            # Calculate the percentage of properties for the language
            language_percentages[lang] = (
                len(language_count.get(lang, set())) / len(unique_properties)
            ) * 100

    return language_percentages


def calculate_language_percentages(properties):
    """
    Calculate the percentage of properties for each language.

    This function takes a list of properties with their corresponding languages and returns a dictionary
    where the keys are the languages and the values are the percentages of properties for each language.

    Args:
        properties (list): A list of tuples containing the property, its value, and its language.

    Returns:
        A dictionary where the keys are the languages and the values are the percentages of properties for each language.

    Notes:
        This function uses a set to store unique properties and a dictionary to store the count of properties for each language.
    """
    # Use a set to store unique properties
    unique_properties = set(prop for prop, _, _ in properties)

    # Use a dictionary to store the count of properties for each language
    language_count = {}

    # Store the total number of properties
    total_properties = len(properties)

    # Iterate over the properties and update the language count dictionary
    for i, (prop, _, lang) in enumerate(properties):
        if lang not in language_count:
            language_count[lang] = set()
        language_count[lang].add(prop)

    print("\n")

    # Calculate the percentage of properties for each language
    if not unique_properties:
        return {}

    # Initialize an empty dictionary to store the language percentages
    language_percentages = {}

    # Iterate over the language count dictionary and calculate the percentages
    for lang, props in language_count.items():
        language_percentages[lang] = (len(props) / len(unique_properties)) * 100

    return language_percentages
