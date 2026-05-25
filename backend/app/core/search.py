import os
from elasticsearch import Elasticsearch
from typing import List, Dict, Any

ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
INDEX_NAME = "voters"

es = Elasticsearch(ELASTICSEARCH_URL)

def create_index():
    """Creates the voter index."""
    settings = {
        "mappings": {
            "properties": {
                "voter_id": {"type": "keyword"},
                "full_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {"type": "keyword"}
                    }
                },
                "job_id": {"type": "keyword"},
                "confidence": {"type": "float"},
                "structured_data": {"type": "object"}
            }
        }
    }
    if not es.indices.exists(index=INDEX_NAME):
        es.indices.create(index=INDEX_NAME, body=settings)

def index_voter(voter_id: str, full_name: str, job_id: str, confidence: float, structured_data: Dict[str, Any]):
    """Indexes a single voter record."""
    doc = {
        "voter_id": voter_id,
        "full_name": full_name,
        "job_id": job_id,
        "confidence": confidence,
        "structured_data": structured_data
    }
    es.index(index=INDEX_NAME, id=voter_id, document=doc)

def search_voters(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Searches for voters using fuzzy matching on full_name or voter_id."""
    body = {
        "size": limit,
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["full_name^2", "voter_id"],
                "fuzziness": "AUTO"
            }
        }
    }
    response = es.search(index=INDEX_NAME, body=body)
    return [hit["_source"] for hit in response["hits"]["hits"]]
