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


def get_missing_translations(properties, languages):
    """
    Find properties that do not have translations in the given languages.

    This function takes a list of properties with their corresponding languages and returns a dictionary
    where the keys are the properties and the values are the languages that do not have translations.

    Args:
        properties (list): A list of tuples containing the property, its value, and its language.
        languages (list): A list of languages to check for translations.

    Returns:
        A dictionary where the keys are the properties and the values are the languages that do not have translations.

    Notes:
        This function uses a set to store unique properties and a dictionary to store the translations for each property.
    """
    # Use a set to store unique properties
    unique_properties = set(prop for prop, _, _ in properties)

    # Use a dictionary to store the translations for each property
    property_translations = {}
    for prop, _, lang in properties:
        if prop not in property_translations:
            property_translations[prop] = set()
        property_translations[prop].add(lang)

    # Find properties that do not have translations in the given languages
    missing_translations = {}
    for prop, translations in property_translations.items():
        missing_languages = set(languages) - translations
        if missing_languages:
            missing_translations[prop] = missing_languages

    return missing_translations


def get_missing_translations_for_all_languages(properties):
    """
    Find properties that do not have translations in all languages.

    This function takes a list of properties with their corresponding languages and returns a dictionary
    where the keys are the properties and the values are the languages that do not have translations.

    Args:
        properties (list): A list of tuples containing the property, its value, and its language.

    Returns:
        A dictionary where the keys are the properties and the values are the languages that do not have translations.

    Notes:
        This function uses a set to store unique properties and a dictionary to store the translations for each property.
    """
    # Use a set to store unique properties
    unique_properties = set(prop for prop, _, _ in properties)

    # Use a dictionary to store the translations for each property
    property_translations = {}
    for prop, _, lang in properties:
        if prop not in property_translations:
            property_translations[prop] = set()
        property_translations[prop].add(lang)

    # Find properties that do not have translations in all languages
    all_languages = set(lang for _, _, lang in properties)
    missing_translations = {}
    for prop, translations in property_translations.items():
        missing_languages = all_languages - translations
        if missing_languages:
            missing_translations[prop] = missing_languages

    return missing_translations


def get_properties_without_translations(properties):
    """
    Find properties that do not have translations in all languages.

    This function takes a list of properties with their corresponding languages and returns a dictionary
    where the keys are the languages and the values are the properties that do not have translations in those languages.

    Args:
        properties (list): A list of tuples containing the property, its value, and its language.

    Returns:
        A dictionary where the keys are the languages and the values are the properties that do not have translations in those languages.
    """
    # Get all languages from the properties
    languages = set(lang for _, _, lang in properties)

    # Create a dictionary to store the languages for each property
    properties_without_translations = {}
    for prop, _, lang in properties:
        if prop not in properties_without_translations:
            properties_without_translations[prop] = set()
        properties_without_translations[prop].add(lang)

    # Find properties that do not have translations in all languages
    missing_translations = {}
    for prop, langs in properties_without_translations.items():
        missing_langs = languages - langs
        for lang in missing_langs:
            if lang not in missing_translations:
                missing_translations[lang] = set()
            missing_translations[lang].add(prop)

    return missing_translations


def get_properties_without_translations_in_languages(properties, languages):
    """
    Find properties that do not have translations in specific languages.

    This function takes a list of properties with their corresponding languages and a list of languages,
    and returns a dictionary where the keys are the languages and the values are the properties that do not have translations in those languages.

    Args:
        properties (list): A list of tuples containing the property, its value, and its language.
        languages (list): A list of languages.

    Returns:
        A dictionary where the keys are the languages and the values are the properties that do not have translations in those languages.
    """
    # Create a dictionary to store the languages for each property
    properties_without_translations = {}
    for prop, _, lang in properties:
        if prop not in properties_without_translations:
            properties_without_translations[prop] = set()
        properties_without_translations[prop].add(lang)

    # Find properties that do not have translations in the specified languages
    missing_translations = {}
    for lang in languages:
        for prop, langs in properties_without_translations.items():
            if lang not in langs:
                if lang not in missing_translations:
                    missing_translations[lang] = set()
                missing_translations[lang].add(prop)

    return missing_translations
