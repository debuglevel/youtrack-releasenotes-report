import logging, logging.config, yaml
import argparse
from pprint import pprint

import generator
import youtrack_lib

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logging.config.dictConfig(yaml.load(open("logging-config.yaml", 'r')))


def main(youtrack_url: str, hub_url: str, token: str, output_basename: str, title: str, field_name: str,
         field_value: str):
    # pdf_filename = f"out/{output_basename}.pdf"

    logger.info(f"Creating YouTrack Client...")
    youtrack_client = youtrack_lib.create_client(youtrack_url, hub_url, token)

    logger.info(f"Getting issues with '{field_name}'='{field_value}'...")
    issues_by_field = youtrack_lib.get_issues_by_field(youtrack_client, field_name, field_value)
    logger.info(f"Got {len(issues_by_field)} issues")

    logger.info(f"Getting Markdown...")
    markdown_string = generator.get_markdown(issues_by_field, title)
    generator.write_markdown_file("out/intermediate.md", markdown_string)
    # generator.generate_pdf_from_markdown(markdown_string, pdf_filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='YouTrack Release Notes Report')

    parser.add_argument('youtrack_url', type=str,
                        help='YouTrack URL (e.g. https://youtrack.jetbrains.com/api)')

    parser.add_argument('hub_url', type=str,
                        help='Hub URL (e.g. https://hub.jetbrains.com/api/rest)')

    parser.add_argument('token', type=str,
                        help='Token to login')

    parser.add_argument('--field-name', type=str,
                        help='Issue field name to search for (e.g. "Development Package")')

    parser.add_argument('--field-value', type=str,
                        help='Issue field value to search for (e.g. "Package 1")')

    parser.add_argument('--output-basename', type=str, default="release_notes",
                        help='Name of the output files (e.g. "release" for "release.pdf")')

    parser.add_argument('--title', type=str, default="Release Notes",
                        help='Title on the front matter')

    args = parser.parse_args()

    main(args.youtrack_url, args.hub_url, args.token, args.output_basename, args.title, args.field_name,
         args.field_value)
