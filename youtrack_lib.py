import logging
from youtrack.connection import Connection as YouTrack
from main import process_attachments

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
