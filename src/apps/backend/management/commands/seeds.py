import json
import os
from django.core.management.base import BaseCommand
from src.apps.backend.models import Fingerprint, Tool


class Command(BaseCommand):
    help = "Pass to --results a path to collected results. Default value is 'results'."

    def handle(self, *args, **options):
        results_path = options.get("results") or "results"
        results = parse_results_directory(results_path)

        for res in results:
            fp, _ = Fingerprint.objects.get_or_create(
                hash=res["fp"]["ja3_hash"],
                kind=Fingerprint.Kind.JA3.value,
                defaults={
                    "value": res["fp"]["ja3_text"]
                }
            )
            fpn, _ = Fingerprint.objects.get_or_create(
                hash=res["fp"]["ja3n_hash"],
                kind=Fingerprint.Kind.JA3N.value,
                defaults={
                    "value": res["fp"]["ja3n_text"]
                }
            )
            parsed_tool, _ = Tool.objects.get_or_create(
                system=res["system"].split("/")[-1],
                name=res["tool_name"],
                version=res["tool_version"],
                kind=Tool.Kind.HTTP_CLIENT.value
            )
            parsed_tool.fingerprints.add(fp, fpn)


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
