import elastic
import json
from unidecode import unidecode

INPUT = "./gpt_adverse_articles.json"
MAIN_INDEX = elastic.INDEX_NAME_MAIN
PROGRESS_INDEX = elastic.INDEX_NAME_AMS_PROGRESS
MAPPINGS = elastic.MAPPINGS_MAIN

elastic.test_connection()
elastic.create_index(MAIN_INDEX, MAPPINGS)
# mappings are empty string here, progress does not need any mapping
elastic.create_index(PROGRESS_INDEX, "")


def create_locations(record, locations):
    for location in locations:
         record["locations"][location] = 1
    return record



def update_locations(record, locations):
    current_locations = record["locations"] if "locations" in record else {}
    for location in locations:
        if location in current_locations:
             current_locations[location] += 1
        else:
             current_locations[location] = 1
    record["locations"] = current_locations
    return record

def update_aliases(record: dict, aliases: list):
    for alias in aliases:
        if alias not in record["aliases"]:
            record["aliases"].append(alias)
        alias_ascii = unidecode(alias)
        if alias_ascii not in record["aliases_ascii"]:
            record["aliases_ascii"].append(alias_ascii)
    return record




def length_is_similar(stored_name: str, new_name: str):
    # there can be maximum of 2 characters difference in lenght to declare that the names are for the same people
    LENGTH_SIMILARITY_TRESHOLD = 2
    len_difference = abs(len(stored_name) - len(new_name))
    if len_difference > LENGTH_SIMILARITY_TRESHOLD:
        return False
    return True


# update all known aliases for entity. The most common alias is then used as the main name for the entity
def update_aliases_count(record: dict, alias: str):
    current_aliases = record["aliases_count"]
    if alias in current_aliases:
        current_aliases[alias] += 1
    else:
        current_aliases[alias] = 1
    most_common_name = max(current_aliases, key=lambda k: current_aliases[k])
    record["name"] = most_common_name
    record["name_ascii"] = unidecode(most_common_name)
    return record


def insert_or_update_entities(entities: list, entity_type: str, locations: list, source: str):
    for entity in entities:
        # check if entity is already in db
        document = elastic.get_document_by_name(entity)
        # if elastic returned a document but the length of name are not similar, treat it as new doc.
        if document is None or not length_is_similar(document["_source"]["name"], entity):
            print("New entity " + entity)
            # new entity
            new_record = {
                "name": entity,
                "name_ascii": unidecode(entity),
                "type": entity_type,
                "aliases": [],
                "aliases_ascii": [],
                "aliases_count": {},
                "information_source": ["ams"],
                "locations": {},
                "ams_articles": [source],
                "pep_record": [],
                "sl_record": []
            }
            new_record = create_locations(new_record, locations)
            # init aliases count
            new_record["aliases_count"][entity] = 1
            elastic.insert_main_document(new_record)
        else:
            print("Existing entity " + document["_source"]["name"] + " matched with " + entity)
            doc_id = document["_id"]
            body = update_locations(document["_source"], locations)
            body = update_aliases(body, [entity])
            body = update_aliases_count(body, entity)
            body["ams_articles"].append(source)
            if "ams" not in body["information_source"]:
                body["information_source"].append("ams")
            elastic.update_main_document(body, doc_id)
            
            


for line in open(INPUT, "r", encoding="utf-8"):
    line = line.rstrip()
    doc = json.loads(line)
    if elastic.document_was_parsed(doc["link"], PROGRESS_INDEX):
        continue
    if "gpt3_entities" in doc:
        people = doc["gpt3_entities"]["names"] if "names" in doc["gpt3_entities"] else []
        people = people if type(people) == list else []

        organizations = doc["gpt3_entities"]["organizations"] if "organizations" in doc["gpt3_entities"] else []
        organizations = organizations if type(organizations) == list else []

        locations = doc["gpt3_entities"]["geographical_places"] if "geographical_places" in doc["gpt3_entities"] else []
        locations = locations if type(locations) == list else []

        insert_or_update_entities(people, "person", locations, doc["link"])
        insert_or_update_entities(organizations, "organization", locations, doc["link"])
        elastic.refresh()
    elastic.insert_progress(doc["link"], PROGRESS_INDEX)
