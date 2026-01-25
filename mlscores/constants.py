#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Constants for mlscores configuration."""

from typing import Final

# SPARQL configuration
DEFAULT_SPARQL_ENDPOINT: Final[str] = "https://query.wikidata.org/sparql"
BATCH_SIZE: Final[int] = 100
MAX_RETRIES: Final[int] = 5
INITIAL_SLEEP_SECONDS: Final[int] = 1
BACKOFF_MULTIPLIER: Final[int] = 2
PROGRESS_BAR_TOTAL: Final[int] = 100

# URI patterns for Wikidata
WIKIDATA_PROPERTY_PREFIX: Final[str] = "http://www.wikidata.org/prop/direct/"
WIKIDATA_ENTITY_PREFIX: Final[str] = "http://www.wikidata.org/entity/"
WIKIDATA_ITEM_PREFIX: Final[str] = "http://www.wikidata.org/entity/Q"

# Default labels
DEFAULT_NO_LABEL: Final[str] = "No label"
DEFAULT_UNKNOWN_LANGUAGE: Final[str] = "Unknown language"

# Cache configuration
DEFAULT_CACHE_TTL_SECONDS: Final[int] = 3600  # 1 hour
