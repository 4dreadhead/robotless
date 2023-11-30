import json
import os
from peewee import PostgresqlDatabase
from dotenv import load_dotenv
from lib.db.tables import *

load_dotenv()


def run(results_path='/tmp/results'):
    connector = PostgresqlDatabase(
        os.getenv("PG_DATABASE_NAME"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT")
    )
    connector.connect()
    connector.create_tables([Fingerprint, Tool, Tool.fingerprints.get_through_model()])

    results = parse_results_directory(results_path)

    for res in results:
        fp, fp_created = Fingerprint.get_or_create(
            hash=res["fp"]["ja3_hash"],
            defaults={
                "kind": Fingerprint.Kind.JA3.value,
                "value": res["fp"]["ja3_text"]
            }
        )
        parsed_tool = Tool.create(
            system=res["system"].split("/")[-1],
            name=res["tool_name"],
            version=res["tool_version"],
            fingerprint=fp,
            kind=Tool.Kind.HTTP_CLIENT.value
        )
        parsed_tool.fingerprints.add(fp)



def json_from_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


def parse_results_directory(directory_path):
    result = []

    for system_folder in os.listdir(directory_path):
        system_path = os.path.join(directory_path, system_folder)
        if not os.path.isdir(system_path):
            continue

        for tool_json_file in os.listdir(system_path):
            tool_json_path = os.path.join(system_path, tool_json_file)

            if not (os.path.isfile(tool_json_path) and tool_json_file.endswith('.json')):
                continue

            tool_name, tool_version = tool_json_file.rsplit('-', 1)
            tool_version = tool_version.rstrip('.json')

            fp = json_from_file(tool_json_path)

            result.append({
                "fp": fp,
                "tool_name": tool_name,
                "tool_version": tool_version,
                "system": system_path
            })

    return result
