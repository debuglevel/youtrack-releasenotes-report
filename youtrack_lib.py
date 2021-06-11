import logging
from youtrack.connection import Connection as YouTrack
import urllib.request

logger = logging.getLogger(__name__)


def get_issues_by_subsystem(subsystem, issues):
    logger.debug(f"Getting issues for subsystem '{subsystem}' from {len(issues)} issues...")
    filtered_issues = set(filter(lambda issue: issue["Teilsystem"] == subsystem, issues))
    logger.debug(f"Got {len(filtered_issues)} issues for subsystem '{subsystem}' from {len(issues)} issues")
    return filtered_issues


def get_subsystems_from_issues(issues):
    logger.debug(f"Getting subsystems from {len(issues)} issues...")
    subsystems = list(set(map(lambda issue: issue["Teilsystem"], issues))) # unique (set), but ordered (list)
    logger.debug(f"Got {len(subsystems)} subsystems from {len(issues)} issues...")
    return subsystems


def process_attachments(youtrack, issue):
    logger.debug(f"Processing attachments for issue {issue['id']} (if any)...")
    attachments = youtrack.getAttachments(issue['id'])

    for attachment in attachments:
        logger.debug(f"Processing attachment '{attachment['name']}' for issue {issue['id']}...")
        url = attachment["url"]
        original_name = attachment['name']
        destination_name = f"{issue['id']}-{attachment['id']}-{attachment['name']}"
        destination_file = f"out/{destination_name}"

        if "Release Notes" not in issue:
            logger.debug(f"Skipping '{attachment['name']}' as no Release Notes found...")
            continue

        if original_name not in issue["Release Notes"]:
            logger.debug(f"Skipping '{attachment['name']}' as not referenced in {issue['id']} Release Notes...")
            continue

        logger.debug(f"Downloading {url} to {destination_file} ...")
        urllib.request.urlretrieve(url, destination_file)

        logger.debug(f"Rewriting markdown to point to downloaded file...")
        issue["Release Notes"] = issue["Release Notes"].replace(original_name, destination_name)


def get_issues(youtrack):
    issues = youtrack.getAllIssues()

    for issue in issues:
        process_attachments(youtrack, issue)

    filtered_issues = filter(lambda issue: "OT" in issue["id"], issues)
    return filtered_issues


def get_issues_by_field(youtrack, field_name, field_value):
    logger.debug(f"Getting issues for '{field_name}'='{field_value}'")

    issues = get_issues(youtrack)

    filtered_issues = []
    for issue in issues:
        try:
            if issue[field_name] == field_value:
                logger.debug(f"Adding {issue['id']} because '{field_name}'='{field_value}'")
                filtered_issues.append(issue)
            else:
                logger.debug(
                    f"Not adding {issue['id']} because '{field_name}'!='{field_value} (but f{issue[field_name]})'")
        except KeyError:
            # CAVEAT: default values seem to be missing here :-(
            logger.debug(f"Not adding {issue['id']} because '{field_name}' is missing")

    logger.debug(f"Got {len(filtered_issues)} issues for '{field_name}'='{field_value}'")
    return filtered_issues


def login(host, username, password):
    logger.debug(f"Logging in at '{host}' as '{username}'...")
    youtrack = YouTrack(host, login=username, password=password)
    logger.debug("Logged in")
    return youtrack
