"""Shared SPARQL query builders used by FastAPI and Pyodide runtimes."""

from typing import List


def build_values_clause(uris: List[str]) -> str:
    return " ".join([f"(<{uri}>)" for uri in uris])


def build_properties_and_values_query(item_id: str) -> str:
    return f"""
    PREFIX wd: <http://www.wikidata.org/entity/>
    SELECT ?property ?value WHERE {{
      wd:{item_id} ?property ?value .
    }}
    """


def build_qualifier_properties_and_values_query(item_id: str) -> str:
    return f"""
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


def build_reference_properties_and_values_query(item_id: str) -> str:
    return f"""
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


def build_property_labels_query(property_uris: List[str]) -> str:
    values_clause = build_values_clause(property_uris)
    return f"""
    PREFIX wikibase: <http://wikiba.se/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?p ?propertyLabel ?propertyLabelLang WHERE {{
      VALUES (?p) {{ {values_clause} }}
      OPTIONAL {{
        ?property wikibase:directClaim ?p ;
                  rdfs:label ?propertyLabel .
        BIND(LANG(?propertyLabel) AS ?propertyLabelLang)
      }}
    }}
    """


def build_value_labels_query(value_uris: List[str]) -> str:
    values_clause = build_values_clause(value_uris)
    return f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?v ?valueLabel ?valueLabelLang WHERE {{
      VALUES (?v) {{ {values_clause} }}
      OPTIONAL {{
        FILTER(isIRI(?v))
        ?v rdfs:label ?valueLabel .
        BIND(LANG(?valueLabel) AS ?valueLabelLang)
      }}
    }}
    """
