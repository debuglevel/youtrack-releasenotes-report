import logging
from youtrack.connection import Connection as YouTrack
from main import process_attachments


def get_issues_by_subsystem(subsystem, issues):
    logging.debug(f"Getting issues for subsystem '{subsystem}' from {len(issues)} issues...")
    filtered_issues = set(filter(lambda issue: issue["Teilsystem"] == subsystem, issues))
    logging.debug(f"Got {len(filtered_issues)} issues for subsystem '{subsystem}' from {len(issues)} issues")
    return filtered_issues


def get_subsystems_from_issues(issues):
    logging.debug(f"Getting subsystems from {len(issues)} issues...")
    subsystems = set(map(lambda issue: issue["Teilsystem"], issues))
    logging.debug(f"Got {len(subsystems)} subsystems from {len(issues)} issues...")
    return subsystems


def get_issues(youtrack):
    issues = youtrack.getAllIssues()

    for issue in issues:
        process_attachments(youtrack, issue)

    filtered_issues = filter(lambda issue: "OT" in issue["id"], issues)
    return filtered_issues


def get_issues_by_field(youtrack, field_name, field_value):
    logging.debug(f"Getting issues for '{field_name}'='{field_value}'")

    issues = get_issues(youtrack)

    filtered_issues = []
    for issue in issues:
        try:
            if issue[field_name] == field_value:
                logging.debug(f"Adding {issue['id']} because '{field_name}'='{field_value}'")
                filtered_issues.append(issue)
            else:
                logging.debug(
                    f"Not adding {issue['id']} because '{field_name}'!='{field_value} (but f{issue[field_name]})'")
        except KeyError:
            # CAVEAT: default values seem to be missing here :-(
            logging.debug(f"Not adding {issue['id']} because '{field_name}' is missing")

    logging.debug(f"Got {len(filtered_issues)} issues for '{field_name}'='{field_value}'")
    return filtered_issues


def login(host, username, password):
    logging.debug(f"Logging in at '{host}' as '{username}'...")
    youtrack = YouTrack(host, login=username, password=password)
    logging.debug("Logged in")
    return youtrack
