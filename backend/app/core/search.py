import os
import re
import time
from elasticsearch import Elasticsearch, ConnectionError, helpers
from typing import List, Dict, Any, Optional

try:
    from indic_transliteration import sanscript
    from indic_transliteration.sanscript import transliterate
    INDIC_AVAILABLE = True
except ImportError:
    INDIC_AVAILABLE = False

ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
INDEX_NAME = "voters"

# Define retry parameters
RETRY_ATTEMPTS = 10
RETRY_DELAY_SECONDS = 5

# Initialize es client as None, to be initialized with retry logic
es: Optional[Elasticsearch] = None

def get_es_client() -> Elasticsearch:
    global es
    if es is not None:
        return es
        
    for attempt in range(RETRY_ATTEMPTS):
        try:
            print(f"Attempt {attempt + 1}/{RETRY_ATTEMPTS} to connect to Elasticsearch at {ELASTICSEARCH_URL}")
            # Use request_timeout to prevent hanging indefinitely
            _es_temp = Elasticsearch(ELASTICSEARCH_URL, request_timeout=3)
            if _es_temp.ping():
                es = _es_temp
                print("Successfully connected to Elasticsearch.")
                return es
        except ConnectionError as e:
            print(f"Elasticsearch connection failed: {e}. Retrying in {RETRY_DELAY_SECONDS} seconds...")
            time.sleep(RETRY_DELAY_SECONDS)
        except Exception as e:
            print(f"An unexpected error occurred while connecting to Elasticsearch: {e}. Retrying in {RETRY_DELAY_SECONDS} seconds...")
            time.sleep(RETRY_DELAY_SECONDS)
    raise ConnectionError(f"Failed to connect to Elasticsearch after {RETRY_ATTEMPTS} attempts.")

def create_index():
    """Creates the voter index."""
    _es = get_es_client() # Get a connected client

    settings = {
        "mappings": {
            "properties": {
                "id": {"type": "integer"},
                "voter_id": {"type": "keyword"},
                "candidate_id": {"type": "integer"},
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
    
    for attempt in range(RETRY_ATTEMPTS):
        try:
            if not _es.indices.exists(index=INDEX_NAME):
                _es.indices.create(index=INDEX_NAME, body=settings)
                print(f"Elasticsearch index '{INDEX_NAME}' created successfully.")
            else:
                print(f"Elasticsearch index '{INDEX_NAME}' already exists.")
            return # Index created or already exists, exit loop
        except (ConnectionError, Exception) as e:
            print(f"Elasticsearch operation failed: {e}. Retrying in {RETRY_DELAY_SECONDS} seconds...")
            time.sleep(RETRY_DELAY_SECONDS)
    raise ConnectionError(f"Failed to create Elasticsearch index '{INDEX_NAME}' after {RETRY_ATTEMPTS} attempts.")

def index_voter(id: int, voter_id: str, candidate_id: int, full_name: str, job_id: str, confidence: float, structured_data: Dict[str, Any]):
    """Indexes a single voter record."""
    _es = get_es_client() # Ensure client is connected
    doc = {
        "id": id,
        "voter_id": voter_id,
        "candidate_id": candidate_id,
        "full_name": full_name,
        "job_id": job_id,
        "confidence": confidence,
        "structured_data": structured_data
    }
    # Use the database primary key 'id' as the document ID instead of 'voter_id'
    # to prevent overwrites when EPIC ID is not found.
    _es.index(index=INDEX_NAME, id=str(id), document=doc)

def bulk_index_voters(voters: List[Dict[str, Any]]):
    """Indexes multiple voter records in a single bulk request."""
    _es = get_es_client()
    actions = [
        {
            "_index": INDEX_NAME,
            "_id": str(v["id"]),
            "_source": {
                "id": v["id"],
                "voter_id": v["voter_id"],
                "candidate_id": v["candidate_id"],
                "full_name": v["full_name"],
                "job_id": v["job_id"],
                "confidence": v["confidence"],
                "structured_data": v["structured_data"]
            }
        }
        for v in voters
    ]
    helpers.bulk(_es, actions)

def search_voters(query: str, candidate_id: int, limit: int = 10, skip: int = 0) -> Dict[str, Any]:
    """Searches for voters using fuzzy matching. Transliterates English to Marathi if needed."""
    _es = get_es_client() # Ensure client is connected
    
    # English detection: if query contains any a-zA-Z
    is_english = bool(re.search(r'[a-zA-Z]', query))
    transliterated = None
    
    if is_english and INDIC_AVAILABLE:
        try:
            # Transliterate English (ITRANS) to Devanagari (Marathi)
            transliterated = transliterate(query.lower(), sanscript.ITRANS, sanscript.DEVANAGARI)
        except Exception:
            pass

    must_clauses = [{"term": {"candidate_id": candidate_id}}]
    should_clauses = [
        {
            "multi_match": {
                "query": query,
                "fields": ["full_name^2", "voter_id"],
                "fuzziness": "AUTO"
            }
        }
    ]

    if transliterated:
        should_clauses.append({
            "multi_match": {
                "query": transliterated,
                "fields": ["full_name^2"],
                "fuzziness": "AUTO"
            }
        })

    body = {
        "from": skip,
        "size": limit,
        "query": {
            "bool": {
                "must": must_clauses,
                "should": should_clauses,
                "minimum_should_match": 1
            }
        }
    }
    
    response = _es.search(index=INDEX_NAME, body=body)
    results = [hit["_source"] for hit in response["hits"]["hits"]]
    total = response["hits"]["total"]["value"] if isinstance(response["hits"]["total"], dict) else response["hits"]["total"]
    
    return {
        "results": results,
        "total": total,
        "transliterated": transliterated
    }
