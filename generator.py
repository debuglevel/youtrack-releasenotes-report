import logging
import markdown
from xhtml2pdf import pisa
from shutil import copyfile
from youtrack_lib import get_subsystems_from_issues, get_issues_by_subsystem

logger = logging.getLogger(__name__)

def get_markdown_for_frontmatter(title):
    markdown_string = f"""
# {title}
    """
    return markdown_string


def get_markdown_for_subsystem(subsystem):
    # title = issue['Teilsystem']

    # title = f"{title}"
    title = f"{subsystem}"
    markdown_string = f"""
## {title}
    """

    return markdown_string


def get_markdown_for_issue(issue):
    id = issue['id']
    logger.debug(f"Generating markdown for issue '{id}'...")

    summary = issue['summary']
    # type = issue['Typ']
    # subsystem = issue['Teilsystem']
    # client = issue['Kunde']
    try:
        release_notes = issue['Release Notes']
    except KeyError:
        release_notes = None

    title = f"{id} {summary}"

    if release_notes is not None:
        markdown_string = f"""
### {title}

{release_notes}


        """
    else:
        markdown_string = ""

    logger.debug(f"Generated markdown for issue '{id}'")
    return markdown_string


def get_markdown(issues, title):
    markdown_string = get_markdown_for_frontmatter(title)

    subsystems = get_subsystems_from_issues(issues)
    subsystems.sort()
    for subsystem in subsystems:
        markdown_string += get_markdown_for_subsystem(subsystem)

        subsystem_issues = get_issues_by_subsystem(subsystem, issues)
        sorted_subsystem_issues = sorted(subsystem_issues, key=lambda issue: int(issue["numberInProject"]))
        for subsystem_issue in sorted_subsystem_issues:
            markdown_string += get_markdown_for_issue(subsystem_issue)

    with open("out/intermediate.md", "w", encoding="utf8") as md_file:
        md_file.write(markdown_string)
    return markdown_string


def generate_html_from_markdown(markdown_string):
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


def generate_pdf_from_markdown(markdown_string, output_filename):
    logger.debug(f"Generating PDF '{output_filename}'...")

    html = generate_html_from_markdown(markdown_string)

    result_file = open(output_filename, "w+b")
    pisa_status = pisa.CreatePDF(html, dest=result_file)
    result_file.close()

    # return False on success and True on errors
    return pisa_status.err