import elastic
import json
import csv
from unidecode import unidecode
import pycountry

INPUT = "targets.simple_pep.csv"
MAIN_INDEX = elastic.INDEX_NAME_MAIN
PROGRESS_INDEX = elastic.INDEX_NAME_PEP_PROGRESS
MAPPINGS = elastic.MAPPINGS_MAIN

elastic.test_connection()
elastic.create_index(MAIN_INDEX, MAPPINGS)
# mappings are empty string here, progress does not need any mapping
elastic.create_index(PROGRESS_INDEX, "")


def read_csv(filename):
    records = []
    with open(filename, 'r', encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file)
        headers = next(reader)  # Read the headers
        for row in reader:
            record = {}
            for i, header in enumerate(headers):
                record[header] = row[i]
            records.append(record)
    return records



def length_is_similar(stored_name: str, new_name: str):
    # there can be maximum of 2 characters difference in lenght to declare that the names are for the same people
    LENGTH_SIMILARITY_TRESHOLD = 2
    len_difference = abs(len(stored_name) - len(new_name))
    if len_difference > LENGTH_SIMILARITY_TRESHOLD:
        return False
    return True


def create_locations(record, locations):
    for location in locations:
         record["locations"][location] = 1
    return record

def create_aliases(record, aliases):
    for alias in aliases:
        record["aliases_count"][alias] = 1
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


def insert_or_update_entities(entity: str, entity_type: str, entity_locations: list, entity_aliases: list ,entity_identifier: str):
    # check if entity is already in db
    document = elastic.get_document_by_name(entity)
    if document is None or not length_is_similar(document["_source"]["name"], entity):
        print("New entity " + entity)
        new_record = {
                "name": entity,
                "name_ascii": unidecode(entity),
                "type": entity_type,
                "aliases": entity_aliases,
                "aliases_ascii": [unidecode(a) for a in entity_aliases],
                "aliases_count": {},
                "information_source": ["pep"],
                "locations": {},
                "pep_record": [entity_identifier],
                "sl_record": [],
                "ams_articles": []
        }
        new_record = create_aliases(new_record, entity_aliases)
        new_record = create_locations(new_record, entity_locations)
        new_record = update_aliases(new_record, entity_aliases)
        new_record = update_aliases_count(new_record, entity_aliases)
        elastic.insert_main_document(new_record)
    else:
        print("Existing entity " + document["_source"]["name"] + " matched with " + entity)
        doc_id = document["_id"]
        body = update_locations(document["_source"], entity_locations)
        entity_aliases.append(entity)
        body = update_aliases(body, entity_aliases)
        for al in entity_aliases:
            body = update_aliases_count(body, al)
        if "pep" not in body["information_source"]:
            body["information_source"].append("pep")
        if entity_identifier not in body["pep_record"]:
            body["pep_record"].append(entity_identifier)
        elastic.update_main_document(body, doc_id)




records = read_csv(INPUT)

for rec in records:
    if elastic.document_was_parsed(rec["id"], PROGRESS_INDEX):
        continue
    aliases = rec["aliases"].split(";")
    name = rec["name"]
    locations = []
    rec_type = "person" if rec["schema"].lower() == "person" else "organization"
    for loc in rec["countries"].split(";"):
        country = pycountry.countries.get(alpha_2=loc.upper())
        if country is None:
            country = loc
        else:
            country = country.name
        locations.append(country)
    insert_or_update_entities(name, rec_type, locations, aliases ,rec["id"])
    # does not need to be called every time when inserting peps or sl
    # elastic.refresh()
    elastic.insert_progress(rec["id"], PROGRESS_INDEX)