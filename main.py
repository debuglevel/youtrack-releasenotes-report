import logging, logging.config, yaml
import urllib.request
import argparse
from pprint import pprint

import generator
import youtrack_lib

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logging.config.dictConfig(yaml.load(open("logging-config.yaml", 'r')))


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


def main(url: str, username: str, password: str, output_basename: str, title: str, field_name: str, field_value: str):
    pdf_filename = f"out/{output_basename}.pdf"

    youtrack = youtrack_lib.login(url, username, password)
    issues_by_field = youtrack_lib.get_issues_by_field(youtrack, field_name, field_value)

    markdown_string = generator.get_markdown(issues_by_field, title)
    # generator.generate_pdf_from_markdown(markdown_string, pdf_filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='YouTrack Release Notes Report')

    parser.add_argument('url', type=str,
                        help='YouTrack URL (e.g. http://youtrack.debuglevel.com:8080/)')

    parser.add_argument('username', type=str,
                        help='Username to login')

    parser.add_argument('password', type=str,
                        help='Password to login')

    parser.add_argument('--field-name', type=str,
                        help='Issue field name to search for (e.g. "Development Package")')

    parser.add_argument('--field-value', type=str,
                        help='Issue field value to search for (e.g. "Package 1")')

    parser.add_argument('--output-basename', type=str, default="release_notes",
                        help='Name of the output files (e.g. "release" for "release.pdf")')

    parser.add_argument('--title', type=str, default="Release Notes",
                        help='Title on the front matter')

    args = parser.parse_args()

    main(args.url, args.username, args.password, args.output_basename, args.title, args.field_name, args.field_value)
