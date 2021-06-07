import logging
import tempfile
from youtrack.connection import Connection as YouTrack
from pprint import pprint
import markdown
from xhtml2pdf import pisa
import urllib.request
from shutil import copyfile

logging.basicConfig(level=logging.DEBUG)

def login(host, username, password):
    logging.debug(f"Logging in at '{host}' as '{username}'...")
    youtrack = YouTrack(host, login=username, password=password)
    logging.debug("Logged in")
    return youtrack

def get_project(youtrack):
    return youtrack.getProject("OT")

def process_attachments(youtrack, issue):
    logging.debug(f"Processing attachments for issue {issue['id']}...")
    attachments = youtrack.getAttachments(issue['id'])

    for attachment in attachments:
        logging.debug(f"Processing attachment '{attachment['name']}' for issue {issue['id']}...")
        url = attachment["url"]
        original_name = attachment['name']
        destination_name = f"{issue['id']}-{attachment['id']}-{attachment['name']}"
        destination_file = f"out/{destination_name}"

        logging.debug(f"Downloading {url} to {destination_file} ...")
        urllib.request.urlretrieve(url, destination_file)

        logging.debug(f"Rewriting markdown to point to downloaded file...")

        if "Release Notes" in issue:
            issue["Release Notes"] = issue["Release Notes"].replace(original_name, destination_name)

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
                logging.debug(f"Not adding {issue['id']} because '{field_name}'!='{field_value} (but f{issue[field_name]})'")
        except KeyError:
            # CAVEAT: default values seem to be missing here :-(
            logging.debug(f"Not adding {issue['id']} because '{field_name}' is missing")

    logging.debug(f"Got {len(filtered_issues)} issues for '{field_name}'='{field_value}'")
    return filtered_issues

def get_markdown_for_frontmatter(title):
    markdown = f"""
# {title}
    """
    return markdown

def get_markdown_for_subsystem(subsystem):
    #title = issue['Teilsystem']

    #title = f"{title}"
    title = f"{subsystem}"
    markdown = f"""
## {title}
    """

    return markdown

def get_markdown_for_issue(issue):
    id = issue['id']
    logging.debug(f"Generating markdown for issue '{id}'...")

    summary = issue['summary']
    #type = issue['Typ']
    #subsystem = issue['Teilsystem']
    #client = issue['Kunde']
    try:
        release_notes = issue['Release Notes']
    except KeyError:
        release_notes = None

    title = f"{id} {summary}"

    if release_notes != None:
        markdown = f"""
### {title}
        
{release_notes}


        """
    else:
        markdown = ""

    logging.debug(f"Generated markdown for issue '{id}'")
    return markdown

def get_markdown(issues, title):
    markdown = get_markdown_for_frontmatter(title)

    subsystems = get_subsystems_from_issues(issues)
    for subsystem in subsystems:
        markdown += get_markdown_for_subsystem(subsystem)

        subsystem_issues = get_issues_by_subsystem(subsystem, issues)
        for subsystem_issue in subsystem_issues:
            markdown += get_markdown_for_issue(subsystem_issue)

    with open("out/intermediate.md", "w", encoding="utf8") as md_file:
        md_file.write(markdown)
    return markdown

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

def generate_html_from_markdown(markdown_str):
    logging.debug("Generating HTML from markdown...")
    html = markdown.markdown(markdown_str)
    logging.debug("Generated HTML from markdown")

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

def generate_pdf_from_markdown(markdown, output_filename):
    logging.debug(f"Generating PDF '{output_filename}'...")

    html = generate_html_from_markdown(markdown)

    result_file = open(output_filename, "w+b")
    pisa_status = pisa.CreatePDF(html, dest=result_file)
    result_file.close()

    # return False on success and True on errors
    return pisa_status.err

def main():
    field_name = "Package"
    field_value = "Package 1"
    release_date = "2021-12-14"
    release_title = f"MyTool release notes ({release_date})"
    pdf_name = "out/OT Release Notes 2021-12-24.pdf"
    username = "username"
    password = "password"
    url = "http://youtrack.hosts:8080/"

    youtrack = login(url, username, password)

    issues_by_field = get_issues_by_field(youtrack, field_name, field_value)

    markdown = get_markdown(issues_by_field, release_title)

    generate_pdf_from_markdown(markdown, pdf_name)


if __name__ == '__main__':
    main()
