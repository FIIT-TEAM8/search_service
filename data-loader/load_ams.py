from pymongo import MongoClient, ASCENDING
import json
from unidecode import unidecode

mongo_host = 'localhost'
mongo_port = 27017
username = "root"
password = "example"
connection_string = f"mongodb://{username}:{password}@{mongo_host}:{mongo_port}/"
database_name = 'adversea_search'
collection_name_search = 'adversea_search'
# contains links for articles which data has already been processed
collection_name_links = 'adversea_search_parsed_links'

INPUT = "./gpt_adverse_articles.json"


client = MongoClient(connection_string)
database = client[database_name]
collection_search = database[collection_name_search]
collection_links = database[collection_name_links]
collection_search.create_index([('name', ASCENDING)], unique=True)
collection_search.create_index([('name_ascii', ASCENDING)])
collection_links.create_index([('link', ASCENDING)], unique=True)


# will raise exception if the connection is not valid
def check_connection():
    try:
        client.server_info()
        return
    except Exception as e:
        print(e)
        print("Mongo connection exception. Exitting...")
        exit(1)


# return set of parsed links
def get_all_parsed_links():
    link_set = set()
    for document in collection_links.find():
        link_set.add(document["link"])
    return link_set


def update_locations(record, locations):
    current_locations = record["locations"] if "locations" in record else {}
    for location in locations:
        if location in current_locations:
             current_locations[location] += 1
        else:
             current_locations[location] = 1
    record["locations"] = current_locations
    if "ams" not in record["information_source"]:
        record["information_source"].append("ams")
    return record

def create_locations(record, locations):
    for location in locations:
         record["locations"][location] = 1
    return record

def insert_or_update_entities(entities: list, entity_type: list, locations: list):
    for entity in entities:
            # check if entity is already in db
            document = collection_search.find_one({"name": entity})
            # new entity
            if document is None:
                new_record = {
                    "name": entity,
                    "name_ascii": unidecode(entity),
                    "type": entity_type,
                    "information_source": ["ams"],
                    "locations": {}
                }
                new_record = create_locations(new_record, locations)
                collection_search.insert_one(new_record)
            else:
                document = update_locations(document, locations)
                if "ams" not in document["information_source"]:
                    document["information_source"].append("ams")
                collection_search.update_one({"name": entity}, {"$set": {"locations": document["locations"], "information_source": document["information_source"]}})

        
check_connection()


parsed_links = get_all_parsed_links()

for line in open(INPUT, "r", encoding="utf-8"):
    line = line.rstrip()
    doc = json.loads(line)
    if doc["link"] in parsed_links:
        continue

    # for every person, insert it into database
    if "gpt3_entities" in doc: # and "names" in doc["gpt3_entities"] and type(doc["gpt3_entities"]["names"]) == list:
        people = doc["gpt3_entities"]["names"] if "names" in doc["gpt3_entities"] else []
        people = people if type(people) == list else []
        people = [person.lower() for person in people]

        organizations = doc["gpt3_entities"]["organizations"] if "organizations" in doc["gpt3_entities"] else []
        organizations = organizations if type(organizations) == list else []
        organizations = [org.lower() for org in organizations]

        locations = doc["gpt3_entities"]["geographical_places"] if "geographical_places" in doc["gpt3_entities"] else []
        locations = locations if type(locations) == list else []

        insert_or_update_entities(people, "person", locations)
        insert_or_update_entities(organizations, "organization", locations)

    collection_links.insert_one({"link": doc["link"]})
