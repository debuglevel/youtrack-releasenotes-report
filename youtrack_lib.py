import json
import logging
import urllib.request
import requests
from typing import List, Set
from pprint import pprint

from youtrack_rest_client.api.default import get_issues_id_attachments, get_issues, get_issues_id_custom_fields, \
    get_issues_id_custom_fields_issue_custom_field_id
from youtrack_rest_client import AuthenticatedClient
from youtrack_rest_client.models import Issue, IssueAttachment

logger = logging.getLogger(__name__)


def filter_issues_by_subsystem(issues: List[Issue], subsystem: str) -> List[Issue]:
    logger.debug(f"Getting issues for subsystem '{subsystem}' from {len(issues)} issues...")

    # filtered_issues = set(filter(lambda issue: issue.custom_fields2["Teilsystem"] == subsystem, issues))  # TODO TypeError: unhashable type: 'Issue' (because of set())

    filtered_issues = []
    for issue in issues:
        if issue.custom_fields2["Teilsystem"] == subsystem:
            if issue not in filtered_issues:
                filtered_issues.append(issue)
                logger.debug(f"Added issue '{issue.id_readable}'")

    logger.debug(f"Got {len(filtered_issues)} issues for subsystem '{subsystem}' from {len(issues)} issues")
    return filtered_issues


def get_subsystems_from_issues(issues: List[Issue]) -> List[str]:
    logger.debug(f"Getting subsystems from {len(issues)} issues...")

    # subsystems = list(set(map(lambda issue: issue.custom_fields2["Teilsystem"], issues)))  # unique (set), but ordered (list)

    subsystems = []
    for issue in issues:
        subsystem = issue.custom_fields2["Teilsystem"]
        if subsystem not in subsystems:
            subsystems.append(subsystem)
            logger.debug(f"Added subsystem '{subsystem}'")

    logger.debug(f"Got {len(subsystems)} subsystems from {len(issues)} issues")
    return subsystems


def process_attachments(youtrack_client: AuthenticatedClient, issue: Issue):
    logger.debug(f"Processing attachments for issue {issue.id_readable} (if any)...")
    attachments: List[IssueAttachment] = get_issues_id_attachments.sync(client=youtrack_client, id=issue.id)

    for attachment in attachments:
        logger.debug(f"Processing attachment '{attachment.name}' for issue {issue.id_readable}...")
        # attachment.url is in the form "/api/..." although the base url already contains "/api/"
        url = youtrack_client.youtrack_base_url + "/.." + attachment.url
        original_name = attachment.name
        destination_name = f"{issue.id_readable}-{attachment.id}-{attachment.name}"
        destination_file = f"out/{destination_name}"

        if "Release Notes" not in issue.custom_fields2:
            logger.debug(f"Skipping '{attachment.name}' as no Release Notes found...")
            continue

        logger.debug("Release Notes:")
        pprint(issue.custom_fields2["Release Notes"])

        if original_name not in issue.custom_fields2["Release Notes"]:
            logger.debug(f"Skipping '{attachment.name}' as not referenced in {issue.id_readable} Release Notes...")
            continue

        logger.debug(f"Downloading {url} to {destination_file} ...")

        response = requests.get(url, allow_redirects=True)
        open(destination_file, 'wb').write(response.content)

        logger.debug(f"Rewriting markdown to point to downloaded file...")
        issue.custom_fields2["Release Notes"] = issue.custom_fields2["Release Notes"].replace(original_name,
                                                                                              destination_name)


def get_issues_(youtrack_client: AuthenticatedClient) -> List[Issue]:
    logger.debug(f"Getting all issues...")
    issues = get_issues.sync(client=youtrack_client, top=10000)
    logger.debug(f"Response contains {len(issues)} issues")

    # The IssueCustomField model seems broken and not containing fields like "name" and "value".
    # Workaround: Get custom fields out of the raw response and put them in a custom_fields2 dict.
    # TODO: maybe this can already be get out of get_issues_id_custom_fields.sync_detailed() - API should support this
    for issue in issues:
        logger.debug(f"Getting custom fields for {issue.id_readable}...")
        custom_fields = get_issues_id_custom_fields.sync(client=youtrack_client, id=issue.id)
        logger.debug(f"Response has {len(custom_fields)} custom fields in issue {issue.id_readable}")

        issue.custom_fields2 = dict()

        for custom_field in custom_fields:
            logger.debug(f"Getting custom field {custom_field.id} for {issue.id_readable}...")

            # CAVEAT: Setting fields to include "text" and "markdownText" in value field, which is not queried by default.
            json_bytes = get_issues_id_custom_fields_issue_custom_field_id.sync_detailed(client=youtrack_client,
                                                                                        id=issue.id,
                                                                                        issue_custom_field_id=custom_field.id,
                                                                                        fields="$type,id,name,projectCustomField($type,field($type,fieldType($type,id),id,localizedName,name),id),value($type,id,name,text,markdownText)"
                                                                                         ).content
            json_string = str(json_bytes, 'UTF-8')
            json_object = json.loads(json_string)
            #pprint(json_object)

            # logger.debug(f"Added custom field '{json_object['name']}'='{json_object['value']}'...")
            # json_object.value can be the value or json_object.value.name

            if "value" not in json_object:
                # logger.debug("'value' not available")
                value = "NO_VALUE_KEY"
            elif json_object["value"] is None:
                # logger.debug("'value' is None")
                value = "NOT_SET"
            elif isinstance(json_object["value"], str):
                # logger.debug("'value' is Str")
                value = json_object["value"]
            elif isinstance(json_object["value"], dict):
                # logger.debug("'value' is Dict")

                if "text" in json_object["value"] and isinstance(json_object["value"]["text"], str):
                    # logger.debug("'value.text' is Str")
                    value = json_object["value"]["text"]
                elif "name" in json_object["value"] and isinstance(json_object["value"]["name"], str):
                    # logger.debug("'value.name' is Str")
                    value = json_object["value"]["name"]
                else:
                    value = "UNHANDLED CASE"

                # if "text" not in json_object["value"]:
                #     # logger.debug("'value.name' not available")
                #     value = "NO_VALUE_TEXT_KEY"
                # elif json_object["value"]["text"] is None:
                #     # logger.debug("'value.name' is None")
                #     value = "NOT_SET"
                # elif isinstance(json_object["value"]["text"], str):
                #     # logger.debug("'value.name' is Str")
                #     value = json_object["value"]["text"]
                # else:
                #     logger.debug(
                #         f"'value.text' is neither Str nor Dict nor None (is '{type(json_object['value']['text'])}')")
                #     pprint(json_object)
                #     value = "UNKNOWN TYPE"
                #
                # if "name" not in json_object["value"]:
                #     # logger.debug("'value.name' not available")
                #     value = "NO_VALUE_NAME_KEY"
                # elif json_object["value"]["name"] is None:
                #     # logger.debug("'value.name' is None")
                #     value = "NOT_SET"
                # elif isinstance(json_object["value"]["name"], str):
                #     # logger.debug("'value.name' is Str")
                #     value = json_object["value"]["name"]
                # else:
                #     logger.debug(
                #         f"'value.name' is neither Str nor Dict nor None (is '{type(json_object['value']['name'])}')")
                #     pprint(json_object)
                #     value = "UNKNOWN TYPE"

            else:
                logger.debug(f"'value' is neither Str nor Dict nor None (is '{type(json_object['value'])}')")
                #pprint(json_object)
                value = "UNKNOWN TYPE"

            issue.custom_fields2[json_object["name"]] = value
            logger.debug(f"Added custom field '{json_object['name']}'='{value}' to issue {issue.id_readable}")

        # pprint(issue.custom_fields2)

    logger.debug(f"Got {len(issues)} issues")
    return issues


def get_issues_by_field(youtrack_client: AuthenticatedClient, field_name: str, field_value: str) -> List[Issue]:
    logger.debug(f"Getting issues for '{field_name}'='{field_value}'")

    issues = get_issues_(youtrack_client)

    filtered_issues: List[Issue] = []
    for issue in issues:
        #pprint(issue)
        try:
            if issue.custom_fields2[field_name] == field_value:
                logger.debug(f"Adding {issue.id_readable} because '{field_name}'='{field_value}'")
                filtered_issues.append(issue)
            else:
                logger.debug(
                    f"Not adding {issue.id_readable} because '{field_name}'!='{field_value} (but '{issue.custom_fields2[field_name]}')'")
        except KeyError:
            # CAVEAT: default values seem to be missing here :-(
            logger.debug(f"Not adding {issue.id_readable} because '{field_name}' is missing")

    for filtered_issue in filtered_issues:
        process_attachments(youtrack_client, filtered_issue)

    logger.debug(f"Got {len(filtered_issues)} issues for '{field_name}'='{field_value}'")
    return filtered_issues


def create_client(youtrack_url: str, hub_url: str, token: str) -> AuthenticatedClient:
    logger.debug(f"Creating YouTrack client for '{hub_url}' with Hub '{youtrack_url}'...")
    client = AuthenticatedClient(
        hub_base_url=hub_url,  # "https://hub.jetbrains.com/api/rest",
        youtrack_base_url=youtrack_url,  # "https://youtrack.jetbrains.com/api",
        token=token,
    )
    logger.debug(f"Created YouTrack client for '{hub_url}' with Hub '{youtrack_url}'")
    return client
