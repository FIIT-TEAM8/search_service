import requests
import json
import hashlib
import base64
import urllib
import os

# config
ELASTIC_HOST = os.environ.get("ELASTIC_URI", "http://localhost:9200")
ELASTIC_HOST += "" if ELASTIC_HOST.endswith("/") else "/"


INDEX_NAME_MAIN = "adversea_search"
MAPPINGS_MAIN = "es_mappings/es_mapping_search_main.json"

INDEX_NAME_AMS_PROGRESS = "parsed_ams_links"
MAPPINGS_AMS_PROGRESS = "es_mappings/es_mapping_ams_progress.json"

INDEX_NAME_SL_PROGRESS = "parsed_sl_ids"
MAPPINGS_AMS_PROGRESS = "es_mappings/es_mapping_sl_progress.json"

INDEX_NAME_PEP_PROGRESS = "parsed_pep_ids"
MAPPINGS_AMS_PROGRESS = "es_mappings/es_mapping_pep_progress.json"


def _something_went_wrong(source: str, message: str, code: int):
    print("Status code: ", code)
    raise Exception("Something went wrong while in " +
                    source + ". error: " + message)


def _get_safe_identifier(input_string) -> str:
    return urllib.parse.quote(input_string, safe='')


def test_connection():
    r = requests.get(ELASTIC_HOST)
    if r.status_code >= 200 and r.status_code < 300:
        print(r.text)
        print("Connection succesfull")
    else:
        print("Elastic connection not possible. Exitting...")
        print(r.text)
        exit(1)


def _index_exists(index_name) -> bool:
    r = requests.head(ELASTIC_HOST + index_name)
    if r.status_code == 200:
        print(index_name + " index already present.")
        return True
    elif r.status_code == 404:
        print(index_name + " index does not exist yet.")
        return False
    else:
        print("Something went wrong when checking if" +
              index_name + " index exists.")
        print(r.text)
        return exit(1)


def create_index(index_name: str, mappings: str):
    if _index_exists(index_name):
        return
    if mappings == "":
        m = {}
    else:
        f = open(mappings, "r", encoding="utf-8")
        m = json.load(f)
    r = requests.put(ELASTIC_HOST + index_name, json=m)
    if r.status_code == 200:
        print("Created index " + index_name)
        return
    else:
        _something_went_wrong("creating index " +
                              index_name, r.text, r.status_code)

# use this to check if an article / SL / PEP record is parsed.
# the identifier is URL for article and IDs for SL and PEPs


def document_was_parsed(identifier: str, progress_index_name) -> bool:
    doc_id = _get_safe_identifier(identifier)
    req_url = "{host}{index_name}/_doc/{id}".format(
        host=ELASTIC_HOST, index_name=progress_index_name, id=doc_id)
    r = requests.get(req_url)
    if r.status_code == 200:
        return True
    elif r.status_code == 404:
        return False
    else:
        _something_went_wrong(
            "checking if document is already parsed", r.text, r.status_code)


def insert_progress(identifier: str, progress_index_name: str):
    doc_id = _get_safe_identifier(identifier)
    req_url = "{host}{index_name}/_doc/{id}".format(
        host=ELASTIC_HOST, index_name=progress_index_name, id=doc_id)
    r = requests.put(req_url, json={})
    if r.status_code == 201 or r.status_code == 200:
        return
    else:
        _something_went_wrong("Creating a document", r.text, r.status_code)


# returns existing document or None if we dont have
def get_document_by_name(name: str):
    req_url = "{host}{index_name}/_search".format(
        host=ELASTIC_HOST, index_name=INDEX_NAME_MAIN)
    query = {
        "query": {
            "multi_match": {
                "query": name,
                "fields": ["name"],
                "operator": "and",
                "fuzzy_transpositions": False,
                "fuzziness": "AUTO"
            }
        }
    }
    r = requests.get(req_url, json=query)
    if r.status_code == 200:
        result = r.json()
        total_hits = result["hits"]["total"]["value"]

        if total_hits > 0:
            return result['hits']['hits'][0]
        else:
            return None
    else:
        _something_went_wrong("Getting a document by name", r.text, r.status_code)

def insert_main_document(document: dict):
    req_url = "{host}{index_name}/_doc".format(host=ELASTIC_HOST, index_name=INDEX_NAME_MAIN)
    r = requests.post(req_url, json=document)
    if r.status_code == 201:
        return
    else:
        _something_went_wrong("Inserting a new document", r.text, r.status_code)
        
def update_main_document(update_body: dict, identifier: str):
    req_url = "{host}{index_name}/_doc/{doc_id}".format(host=ELASTIC_HOST, index_name=INDEX_NAME_MAIN, doc_id=_get_safe_identifier(identifier))
    r = requests.post(req_url, json=update_body)
    if r.status_code == 200:
        return
    else:
        _something_went_wrong("Updating a document", r.text, r.status_code)

# this has to be called after every single article insert, otherwise common names might not get updated but duplicated records will exist
def refresh():
    req_url = "{host}{index_name}/_refresh".format(host=ELASTIC_HOST, index_name=INDEX_NAME_MAIN)
    r = requests.post(req_url)
    if r.status_code == 200:
        return
    else: 
        _something_went_wrong("Refreshing cache", r.text, r.status_code)