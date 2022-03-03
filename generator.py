import logging
from typing import List

import markdown
from xhtml2pdf import pisa
from shutil import copyfile

from youtrack_rest_client.models import Issue

from youtrack_lib import get_subsystems_from_issues, filter_issues_by_subsystem

logger = logging.getLogger(__name__)


def get_markdown(issues: List[Issue], title: str, field_name: str):
    markdown_string = get_markdown_for_frontmatter(title)

    subsystems = get_subsystems_from_issues(issues)
    subsystems.sort()
    for subsystem in subsystems:
        markdown_string += get_markdown_for_subsystem(subsystem)

        subsystem_issues = filter_issues_by_subsystem(issues, subsystem)
        sorted_subsystem_issues = sorted(subsystem_issues, key=lambda issue: int(issue.number_in_project))
        for subsystem_issue in sorted_subsystem_issues:
            markdown_string += get_markdown_for_issue(subsystem_issue, field_name)

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


def get_markdown_for_issue(issue: Issue, field_name: str):
    id = issue.id_readable
    logger.debug(f"Generating markdown for issue '{id}'...")

    summary = issue.summary
    # type = issue['Typ']
    # subsystem = issue['Teilsystem']
    # client = issue['Kunde']
    try:
        content = issue.custom_fields2[field_name]
    except KeyError:
        content = None

    title = f"{id} {summary}"

    if content is not None:
        markdown_string = f"""
## {title}

{content}


        """
    else:
        markdown_string = ""

    logger.debug(f"Generated markdown for issue '{id}'")
    return markdown_string


def generate_html_from_markdown(markdown_string: str):
    logger.debug("Generating HTML from markdown...")
    html = markdown.markdown(markdown_string)
    logger.debug("Generated HTML from markdown")

    with open("out/intermediate.html", "w", encoding="utf8") as html_file:
        html_file.writelines("""
<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="print.css">
</head>
<body>
""")
        html_file.write(html)
        html_file.writelines("""
</body>
""")

        copyfile("print.css", "out/print.css")

    return html


def generate_pdf_from_markdown(markdown_string: str, output_filename: str):
    logger.debug(f"Generating PDF '{output_filename}'...")

    html = generate_html_from_markdown(markdown_string)

    result_file = open(output_filename, "w+b")
    pisa_status = pisa.CreatePDF(html, dest=result_file)
    result_file.close()

    # return False on success and True on errors
    return pisa_status.err
