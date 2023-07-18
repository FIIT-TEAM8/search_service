from pymongo import MongoClient, ASCENDING
import json
import csv
from unidecode import unidecode
import pycountry


mongo_host = 'localhost'
mongo_port = 27017
username = "root"
password = "example"
connection_string = f"mongodb://{username}:{password}@{mongo_host}:{mongo_port}/"
database_name = 'adversea_search'
collection_name_search = 'adversea_search'
collection_pep_ids = 'adversea_search_pep_parsed_ids'

INPUT = "targets.simple_pep.csv"


client = MongoClient(connection_string)
database = client[database_name]
collection_search = database[collection_name_search]
collection_progress = database[collection_pep_ids]
collection_search.create_index([('name', ASCENDING)], unique=True)
collection_search.create_index([('name_ascii', ASCENDING)])
collection_progress.create_index([('pepid', ASCENDING)], unique=True)

# will raise exception if the connection is not valid
def check_connection():
    try:
        client.server_info()
        return
    except Exception as e:
        print(e)
        print("Mongo connection exception. Exitting...")
        exit(1)


def get_all_parsed_ids():
    link_set = set()
    for document in collection_progress.find():
        link_set.add(document["pepid"])
    return link_set

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




# check_connection()

records = read_csv(INPUT)
parsed_pepids = get_all_parsed_ids()


for rec in records:
    if rec["id"] in parsed_pepids:
        continue
    name = rec["name"].lower()
    document = collection_search.find_one({"name_ascii": name})
    if document == None:
        locations = {}
        for loc in rec["countries"].split(";"):
            country = pycountry.countries.get(alpha_2=loc.upper())
            if country is None:
                country = loc
            else:
                country = country.name
            locations[country] = 1
        new_record = {
                    "name": name,
                    "name_ascii": unidecode(name),
                    "type": "person" if rec["schema"].lower() == "person" else "organization",
                    "information_source": ["pep"],
                    "locations": locations
                }
        collection_search.insert_one(new_record)
    else:
        if "pep" not in document["information_source"]:
            document["information_source"].append("pep")
        for loc in rec["countries"].split(";"):
            country = pycountry.countries.get(alpha_2=loc.upper())
            if country is None:
                country = loc
            else:
                country = country.name
            if country in document["locations"]:
                document["locations"][country] += 1
            else:
                document["locations"][country] = 1
        collection_search.update_one({"name": name}, {"$set": {"locations": document["locations"], "information_source": document["information_source"]}})
    
    collection_progress.insert_one({"pepid": rec["id"]})
        
