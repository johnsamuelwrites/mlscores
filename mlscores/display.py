#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from rich.console import Console
from rich.table import Table


def print_language_percentages(percentages, title):
    """
    Print language percentages as a table.

    This function takes a dictionary of language percentages and a title, and prints a table
    showing the language percentages.

    Args:
        percentages (dict): A dictionary where the keys are the languages and the values are the percentages.
        title (str): The title of the table.

    Notes:
        This function uses the `Console` and `Table` classes from the `rich` library to print the table.
    """
    # Create a console instance
    console = Console()

    # Create a table instance with the given title
    table = Table(title=title)

    # Add columns to the table for language and percentage
    table.add_column("Language", justify="left", style="cyan")
    table.add_column("Percentage", justify="right", style="magenta")

    # Iterate over the language percentages and add rows to the table
    for language, percentage in percentages.items():
        table.add_row(language, f"{percentage:.2f}%")

    # Print the table to the console
    console.print(table)


def print_item_language_table(data, title):
    """
    Prints a table of language and languages.

    This function takes a list of tuples containing languages and their corresponding items,
    and prints a table with the languages and items.

    Args:
        data (list of tuples): Table data, where each tuple contains a language and a list of items.

    Returns:
        None
    """
    # Initialize a console object to print the table
    console = Console()

    # Create a table with a title
    table = Table(title=title)

    # Add columns to the table
    table.add_column("Languages", justify="left", style="cyan")
    table.add_column("Items", justify="left", style="magenta")

    # Iterate over the data and add rows to the table
    for language, items in data.items():
        # Join the list of languages into a string
        items_str = ", ".join(items)
        # Add a row to the table
        items_str = items_str.replace("http://www.wikidata.org/prop/direct/", "")
        items_str = items_str.replace("http://www.wikidata.org/entity/", "")
        table.add_row(language, items_str)

    # Print the table
    console.print(table)
