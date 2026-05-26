import os
import re
from elasticsearch import Elasticsearch
from typing import List, Dict, Any, Optional

try:
    from indic_transliteration import sanscript
    from indic_transliteration.sanscript import transliterate
    INDIC_AVAILABLE = True
except ImportError:
    INDIC_AVAILABLE = False

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

def search_voters(query: str, limit: int = 10) -> Dict[str, Any]:
    """Searches for voters using fuzzy matching. Transliterates English to Marathi if needed."""
    
    # English detection: if query contains any a-zA-Z
    is_english = bool(re.search(r'[a-zA-Z]', query))
    transliterated = None
    
    if is_english and INDIC_AVAILABLE:
        try:
            # Transliterate English (ITRANS) to Devanagari (Marathi)
            transliterated = transliterate(query.lower(), sanscript.ITRANS, sanscript.DEVANAGARI)
        except Exception:
            pass

    if transliterated:
        # Match either original English or transliterated Marathi
        body = {
            "size": limit,
            "query": {
                "bool": {
                    "should": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["full_name^2", "voter_id"],
                                "fuzziness": "AUTO"
                            }
                        },
                        {
                            "multi_match": {
                                "query": transliterated,
                                "fields": ["full_name^2"],
                                "fuzziness": "AUTO"
                            }
                        }
                    ],
                    "minimum_should_match": 1
                }
            }
        }
    else:
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
    results = [hit["_source"] for hit in response["hits"]["hits"]]
    
    return {
        "results": results,
        "transliterated": transliterated
    }
