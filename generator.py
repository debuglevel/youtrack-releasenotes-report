import logging
from typing import List

import markdown
from xhtml2pdf import pisa
from shutil import copyfile

from youtrack_rest_client.models import Issue

from youtrack_lib import get_subsystems_from_issues, filter_issues_by_subsystem

logger = logging.getLogger(__name__)


def get_markdown(issues: List[Issue], title: str):
    markdown_string = get_markdown_for_frontmatter(title)

    subsystems = get_subsystems_from_issues(issues)
    subsystems.sort()
    for subsystem in subsystems:
        markdown_string += get_markdown_for_subsystem(subsystem)

        subsystem_issues = filter_issues_by_subsystem(issues, subsystem)
        sorted_subsystem_issues = sorted(subsystem_issues, key=lambda issue: int(issue.number_in_project))
        for subsystem_issue in sorted_subsystem_issues:
            markdown_string += get_markdown_for_issue(subsystem_issue)

    return markdown_string


def write_markdown_file(filename: str, markdown_string: str):
    with open(filename, "w", encoding="utf8") as md_file:
        md_file.write(markdown_string)


def get_markdown_for_frontmatter(title: str):
    #     markdown_string = f"""
    # # {title}
    #     """
    markdown_string = ""
    return markdown_string


def get_markdown_for_subsystem(subsystem: str):
    # title = issue['Teilsystem']

    # title = f"{title}"
    title = f"{subsystem}"
    markdown_string = f"""
# {title}
    """

    return markdown_string


def get_markdown_for_issue(issue: Issue):
    id = issue.id_readable
    logger.debug(f"Generating markdown for issue '{id}'...")

    summary = issue.summary
    # type = issue['Typ']
    # subsystem = issue['Teilsystem']
    # client = issue['Kunde']
    try:
        release_notes = issue.custom_fields2['Release Notes']
    except KeyError:
        release_notes = None

    if release_notes is not None:
        title = f"{id} {summary}"
        markdown_string = f"""
## {title}

{release_notes}


        """
    else:
        markdown_string = ""

    logger.debug(f"Generated markdown for issue '{id}'")
    return markdown_string
