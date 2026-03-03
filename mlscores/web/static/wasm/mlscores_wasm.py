import json
import urllib.parse
from typing import Dict, List, Optional, Set, Tuple

from pyodide.http import pyfetch

BATCH_SIZE = 25

PROPERTY_PREFIX = "http://www.wikidata.org/prop/direct/"
ENTITY_PREFIX = "http://www.wikidata.org/entity/"
ITEM_PREFIX = "http://www.wikidata.org/entity/Q"

PropertyTuple = Tuple[str, str, str]


def _chunk(items: List[str], size: int) -> List[List[str]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


async def sparql_query(endpoint: str, query: str) -> Dict:
    body = urllib.parse.urlencode({"query": query, "format": "json"})
    response = await pyfetch(
        endpoint,
        method="POST",
        headers={
            "Accept": "application/sparql-results+json",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        },
        body=body,
    )
    if not response.ok:
        text = await response.string()
        raise RuntimeError(f"SPARQL query failed ({response.status}): {text[:250]}")
    return await response.json()


async def get_properties_and_values(item_id: str, endpoint: str) -> Dict:
    query = f"""
    PREFIX wd: <http://www.wikidata.org/entity/>
    SELECT ?property ?value WHERE {{
      wd:{item_id} ?property ?value .
    }}
    """
    return await sparql_query(endpoint, query)


async def get_qualifier_properties_and_values(item_id: str, endpoint: str) -> Dict:
    query = f"""
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wikibase: <http://wikiba.se/ontology#>
    SELECT DISTINCT ?property ?value WHERE {{
      wd:{item_id} ?p ?statement .
      ?statement ?pq ?qualifierValue .
      ?qualifierProperty wikibase:qualifier ?pq .
      BIND(?qualifierProperty AS ?property)
      BIND(?qualifierValue AS ?value)
    }}
    """
    return await sparql_query(endpoint, query)


async def get_reference_properties_and_values(item_id: str, endpoint: str) -> Dict:
    query = f"""
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wikibase: <http://wikiba.se/ontology#>
    PREFIX prov: <http://www.w3.org/ns/prov#>
    SELECT DISTINCT ?property ?value WHERE {{
      wd:{item_id} ?p ?statement .
      ?statement prov:wasDerivedFrom ?referenceNode .
      ?referenceNode ?pr ?referenceValue .
      ?referenceProperty wikibase:reference ?pr .
      BIND(?referenceProperty AS ?property)
      BIND(?referenceValue AS ?value)
    }}
    """
    return await sparql_query(endpoint, query)


async def get_property_labels(property_uris: List[str], endpoint: str) -> List[PropertyTuple]:
    filtered = sorted({uri for uri in property_uris if uri.startswith(PROPERTY_PREFIX)})
    rows = []

    for batch in _chunk(filtered, BATCH_SIZE):
        values = " ".join([f"(<{uri}>)" for uri in batch])
        query = f"""
        PREFIX wikibase: <http://wikiba.se/ontology#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?p ?propertyLabel ?propertyLabelLang WHERE {{
          VALUES (?p) {{ {values} }}
          OPTIONAL {{
            ?property wikibase:directClaim ?p ;
                      rdfs:label ?propertyLabel .
            BIND(LANG(?propertyLabel) AS ?propertyLabelLang)
          }}
        }}
        """
        data = await sparql_query(endpoint, query)
        rows.extend(data.get("results", {}).get("bindings", []))

    return [
        (
            row["p"]["value"],
            row.get("propertyLabel", {}).get("value", "No label"),
            row.get("propertyLabelLang", {}).get("value", "Unknown language"),
        )
        for row in rows
    ]


async def get_value_labels(value_uris: List[str], endpoint: str) -> List[PropertyTuple]:
    filtered = sorted({uri for uri in value_uris if uri.startswith(ITEM_PREFIX)})
    rows = []

    for batch in _chunk(filtered, BATCH_SIZE):
        values = " ".join([f"(<{uri}>)" for uri in batch])
        query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?v ?valueLabel ?valueLabelLang WHERE {{
          VALUES (?v) {{ {values} }}
          OPTIONAL {{
            FILTER(isIRI(?v))
            ?v rdfs:label ?valueLabel .
            BIND(LANG(?valueLabel) AS ?valueLabelLang)
          }}
        }}
        """
        data = await sparql_query(endpoint, query)
        rows.extend(data.get("results", {}).get("bindings", []))

    return [
        (
            row["v"]["value"],
            row.get("valueLabel", {}).get("value", "No label"),
            row.get("valueLabelLang", {}).get("value", "Unknown language"),
        )
        for row in rows
    ]


def calculate_language_percentages(properties: List[PropertyTuple]) -> Dict[str, float]:
    unique_properties = set(prop for prop, _, _ in properties)
    if not unique_properties:
        return {}

    language_count: Dict[str, Set[str]] = {}
    for prop, _, lang in properties:
        language_count.setdefault(lang, set()).add(prop)

    return {
        lang: (len(props) / len(unique_properties)) * 100
        for lang, props in language_count.items()
    }


def calculate_language_percentage_for_languages(
    properties: List[PropertyTuple],
    languages: List[str],
) -> Dict[str, float]:
    unique_properties = set(prop for prop, _, _ in properties)
    language_count: Dict[str, Set[str]] = {}

    for prop, _, lang in properties:
        language_count.setdefault(lang, set()).add(prop)

    result: Dict[str, float] = {}
    for lang in languages:
        if not unique_properties:
            result[lang] = 0.0
        else:
            result[lang] = (len(language_count.get(lang, set())) / len(unique_properties)) * 100
    return result


def get_properties_without_translations(properties: List[PropertyTuple]) -> Dict[str, Set[str]]:
    languages = set(lang for _, _, lang in properties)
    map_prop_to_langs: Dict[str, Set[str]] = {}
    for prop, _, lang in properties:
        map_prop_to_langs.setdefault(prop, set()).add(lang)

    missing: Dict[str, Set[str]] = {}
    for prop, langs in map_prop_to_langs.items():
        for lang in languages - langs:
            missing.setdefault(lang, set()).add(prop)
    return missing


def get_properties_without_translations_in_languages(
    properties: List[PropertyTuple],
    languages: List[str],
) -> Dict[str, Set[str]]:
    map_prop_to_langs: Dict[str, Set[str]] = {}
    for prop, _, lang in properties:
        map_prop_to_langs.setdefault(prop, set()).add(lang)

    missing: Dict[str, Set[str]] = {}
    for target_lang in languages:
        for prop, langs in map_prop_to_langs.items():
            if target_lang not in langs:
                missing.setdefault(target_lang, set()).add(prop)
    return missing


async def calculate_item_scores(
    item_id: str,
    endpoint: str,
    languages: Optional[List[str]],
    include_missing: bool,
) -> Dict:
    properties_values = await get_properties_and_values(item_id, endpoint)
    bindings = properties_values.get("results", {}).get("bindings", [])
    if not bindings:
        raise ValueError(f"No properties found for item {item_id}")

    qualifiers = await get_qualifier_properties_and_values(item_id, endpoint)
    references = await get_reference_properties_and_values(item_id, endpoint)
    bindings.extend(qualifiers.get("results", {}).get("bindings", []))
    bindings.extend(references.get("results", {}).get("bindings", []))

    pairs = [(row["property"]["value"], row["value"]["value"]) for row in bindings]
    property_uris = sorted({prop for prop, _ in pairs})
    value_uris = sorted({value for _, value in pairs if value.startswith("http")})

    property_labels = await get_property_labels(property_uris, endpoint)
    value_labels = await get_value_labels(value_uris, endpoint)

    if languages:
        property_percentages = calculate_language_percentage_for_languages(property_labels, languages)
        value_percentages = calculate_language_percentage_for_languages(value_labels, languages)
        combined_percentages = calculate_language_percentage_for_languages(
            property_labels + value_labels, languages
        )
    else:
        property_percentages = calculate_language_percentages(property_labels)
        value_percentages = calculate_language_percentages(value_labels)
        combined_percentages = calculate_language_percentages(property_labels + value_labels)

    result = {
        "item_id": item_id,
        "property_labels": {"percentages": property_percentages},
        "value_labels": {"percentages": value_percentages},
        "combined": {"percentages": combined_percentages},
    }

    if include_missing:
        if languages:
            missing_properties = get_properties_without_translations_in_languages(property_labels, languages)
            missing_values = get_properties_without_translations_in_languages(value_labels, languages)
        else:
            missing_properties = get_properties_without_translations(property_labels)
            missing_values = get_properties_without_translations(value_labels)

        result["missing_property_translations"] = {
            "by_language": {k: sorted(list(v)) for k, v in missing_properties.items()}
        }
        result["missing_value_translations"] = {
            "by_language": {k: sorted(list(v)) for k, v in missing_values.items()}
        }

    return result


async def calculate_scores_json(payload_json: str) -> str:
    payload = json.loads(payload_json)
    identifiers = payload.get("identifiers", [])
    raw_languages = payload.get("languages", [])
    languages = [lang for lang in raw_languages if lang] or None
    include_missing = bool(payload.get("include_missing", False))
    endpoint = payload.get("endpoint") or "https://query.wikidata.org/sparql"

    results = []
    for item_id in identifiers:
        item_id = item_id.strip()
        if not item_id:
            continue
        results.append(
            await calculate_item_scores(
                item_id=item_id,
                endpoint=endpoint,
                languages=languages,
                include_missing=include_missing,
            )
        )

    return json.dumps({"success": True, "results": results})
