import argparse
import logging
from datetime import datetime
import os


class LogColorFormatter(logging.Formatter):
    '''
    Create a logging formatter to color and format the log output
    '''
    green = "\x1b[32;20m"
    blue = "\x1b[34;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    purple = "\x1b[35;20m"
    reset = "\x1b[0m"
    format = "[%(levelname)s]: %(message)s"

    FORMATS = {
        logging.DEBUG: blue + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: purple + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def main():
    """
    Main entry point for the program
    """
    parser = argparse.ArgumentParser(
        prog='AutoDocExt',
        description=(
            'Application that will automatically generate the rst files '
            'and documentation for Sphinx. The application only supports '
            'python projects, even though sphinx documentation will '
            'support others.'
        ),
        usage=(
            'AutoDoc [-h] <project> [-a ...] [-e <version>] [-c <copyright>] '
            '[-t <theme>] [-s <source_dir>] [-b <build_dir>] '
            '[--extensions ...] [--exclusions ...] [--static ...] '
            '[--templates ...]'
        )
    )
    parser.add_argument(
        'PROJECT', metavar='project',
        type=str,
        help='Name of the project that the application will document'
    )
    parser.add_argument(
        '-a', '--author',
        dest='AUTHOR',
        nargs='+',
        help='Author(s) (space separated) that created the project',
        default=[]
    )
    parser.add_argument(
        '-e', '--version',
        dest='VERSION',
        type=str,
        help='Version for the project',
        default='0.0.0'
    )
    parser.add_argument(
        '-c', '--copyright',
        dest='COPYRIGHT',
        type=int,
        help='Year of the copyright for the project',
        default=datetime.now().year
    )
    parser.add_argument(
        '-t', '--theme', dest='THEME',
        type=str,
        help=(
            'Sphinx docmumentation theme, see '
            'https://www.sphinx-doc.org/en/master/usage/theming.html '
            'for more information.'
        ),
        default='sphinx_rtd_theme'
    )
    parser.add_argument(
        '-s', '--source_dir', dest='SOURCE_DIR',
        type=str,
        help=(
            'Source directory for the project. This will be the site where '
            'project documentation is generated.'
        ),
        default='.'
    )
    parser.add_argument(
        '-b', '--build_dir', dest='BUILD_DIR',
        type=str,
        help=(
            'Directory where the documentation will be built. The value '
            'should be relative to SOURCE_DIR.'
        ),
        default='docs'
    )
    parser.add_argument(
        '--extensions', dest='EXTENSIONS',
        nargs='+',
        help=(
            'Add any Sphinx extension module names here, as strings. '
            'These can be sphinx generated or custom extensions.'
        ),
        default=[]
    )
    parser.add_argument(
        '--templates', dest='TEMPLATES',
        nargs='+',
        help=(
            'Paths that contain templates, these should be relative to '
            'the SOURCE_DIR.'
        ),
        default=[]
    )
    parser.add_argument(
        '--exclusions', dest='EXCLUSIONS',
        nargs='+',
        help=(
            'List of patterns, relative to SOURCE_DIR, that match files '
            'and directories to ignore when looking for source files.'
        ),
        default=[]
    )
    parser.add_argument(
        '--static', dest='STATIC_PATHS',
        nargs='+',
        help=(
            'Add any paths that contain custom static files (such as style '
            'sheets), relative to SOURCE_DIR.'
        ),
        default=[]
    )
    parser.add_argument(
        '-v', '--verbose',
        action='count',
        default=0,
        help='Verbosity level for logging'
    )
    args = parser.parse_args()

    # verbosity starts at 10 and moves to 50
    if args.verbose > 0:
        verbosity = 50 - (10*(args.verbose-1))
    else:
        verbosity = logging.CRITICAL

    # Create the logger. Use the default name for every log that will operate
    # during the use of this application.
    log = logging.getLogger()
    log.setLevel(verbosity)

    # Add a formatter to color the log output and format the text
    handler = logging.StreamHandler()
    handler.setFormatter(LogColorFormatter())
    log.addHandler(handler)

    for root, dirs, files in os.walk("."):
        path = root.split(os.sep)
        print(path)
        print((len(path) - 1) * '---', os.path.basename(root))
        for file in files:
            print(len(path) * '---', file)


if __name__ == "__main__":
    main()
