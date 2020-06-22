import argparse
from autodoc.utility import create_page, generate_rst_tree


def main():
    """
    Main entry point for the program
    """
    parser = argparse.ArgumentParser(
        description='Automatically create the rst files for documentation with Sphinx.'
    )
    parser.add_argument(
        'project',
        type=str,
        help="Name of the root directory of the project to run the documentation creation on."
    )
    parser.add_argument(
        '-d', '--dirs',
        nargs='+',
        default=[],
        help='List of directory names to exclude from the search.'
    )
    parser.add_argument(
        '-f', '--files',
        nargs='+',
        default=[],
        help='List of file names to exclude from the search.'
    )
    parser.add_argument(
        '-s', '--save_dir',
        type=str,
        default="rst_files",
        help="Local directory to save the generated rst files to."
    )

    args = parser.parse_args()

    page = create_page(args.project, args.dirs, args.files)
    if page:
        generate_rst_tree(page, args.save_dir)


if __name__ == "__main__":
    main()