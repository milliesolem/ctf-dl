import argparse
import logging
import sys

from ctfdl.downloader import download_challenges
from ctfdl.utils import list_available_templates

logger = logging.getLogger("ctfdl")

def parse_arguments():
    parser = argparse.ArgumentParser(
        prog='ctf-dl',
        description="Universal CTF Challenge Downloader",
        formatter_class=argparse.RawTextHelpFormatter
    )

    # Login and core settings
    parser.add_argument("-u", "--url", required=True, help="Base URL of the CTF platform (e.g., https://demo.ctfd.io)")
    parser.add_argument("--username", help="Username for login")
    parser.add_argument("--password", help="Password for login")
    parser.add_argument("--token", help="Authentication token")
    parser.add_argument("-o", "--output", default="challenges", help="Output directory to save challenges (default: challenges/)")

    # Templates
    parser.add_argument("--template", help="Path to output template (default: templates/default.md.jinja)")
    parser.add_argument("--folder-template", help="Path to folder structure template (default: templates/folder_structure/default.path.jinja)")

    # Filtering
    parser.add_argument("--categories", nargs="+", help="Only download challenges from specified categories")
    parser.add_argument("--min-points", type=int, help="Minimum points to download")
    parser.add_argument("--max-points", type=int, help="Maximum points to download")

    # Special behaviors
    parser.add_argument("--update", action="store_true", help="Skip challenges that already exist locally")
    parser.add_argument("--dry-run", action="store_true", help="Simulate download without saving files")
    parser.add_argument("--no-attachments", action="store_true", help="Skip downloading attachments")
    parser.add_argument("--parallel", type=int, default=4, help="Number of parallel downloads (default: 4)")

    # Utilities
    parser.add_argument("--list-templates", action="store_true", help="List available templates and exit")

    # Verbosity
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Increase verbosity (-v, -vv)")
    parser.add_argument("-q", "--quiet", action="store_true", help="Reduce output verbosity (show only warnings and errors)")

    return parser.parse_args()

def setup_logging(verbosity, quiet):
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if quiet:
        logger.setLevel(logging.WARNING)
    elif verbosity == 0:
        logger.setLevel(logging.INFO)
    elif verbosity >= 1:
        logger.setLevel(logging.DEBUG)

def main():
    args = parse_arguments()

    setup_logging(args.verbose, args.quiet)

    if args.list_templates:
        list_available_templates()
        sys.exit(0)

    # TODO: load config

    # Validate login options
    if args.token:
        if args.username or args.password:
            logger.error("Provide either --token or --username and --password, not both.")
            sys.exit(1)
    elif args.username and args.password:
        pass
    else:
        logger.error("You must provide either --token or --username and --password.")
        sys.exit(1)

    logger.info("Starting CTF download from %s", args.url)

    download_challenges(
        url=args.url,
        username=args.username,
        password=args.password,
        token=args.token,
        output_dir=args.output,
        template_path=args.template,
        folder_template_path=args.folder_template,
        categories=args.categories,
        min_points=args.min_points,
        max_points=args.max_points,
        update=args.update,
        dry_run=args.dry_run,
        no_attachments=args.no_attachments,
        parallel=args.parallel
    )

    # TODO: optional scoreboard download

    # TODO: save config

    logger.info("All done!")

if __name__ == "__main__":
    main()
