import argparse
import logging
from datetime import datetime
from .tree import generate_tree
from .templates import generate_rst, generate_sphinx, generate_docs_dir
from .artifacts import log_artifacts, destroy
from os import system
from os.path import exists
from sys import platform


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
    parser = argparse.ArgumentParser(prog='docu')
    # Create the subparsers to allow one program to execute multiple paths
    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True

    cleaner = subparsers.add_parser('clean')
    cleaner.add_argument(
        '-s', '--source_dir', dest='SOURCE_DIR',
        type=str,
        help=(
            'Installation directory for the artifacts. This will be the site '
            'where project documentation is generated.'
        ),
        default='.'
    )
    cleaner.add_argument(
        '-v', '--verbose',
        action='count',
        default=0,
        help='Verbosity level for logging'
    )
    
    creator = subparsers.add_parser('create')
    creator.add_argument(
        'PROJECT', metavar='project',
        type=str,
        help='Name of the project that the application will document'
    )
    creator.add_argument(
        '-a', '--author',
        dest='AUTHOR',
        nargs='+',
        help='Author(s) (space separated) that created the project',
        default=[]
    )
    creator.add_argument(
        '-e', '--version',
        dest='VERSION',
        type=str,
        help='Version for the project',
        default='0.0.0'
    )
    creator.add_argument(
        '-c', '--copyright',
        dest='COPYRIGHT',
        type=int,
        help='Year of the copyright for the project',
        default=datetime.now().year
    )
    creator.add_argument(
        '-t', '--theme', dest='THEME',
        type=str,
        help=(
            'Sphinx docmumentation theme, see '
            'https://www.sphinx-doc.org/en/master/usage/theming.html '
            'for more information.'
        ),
        default='sphinx_rtd_theme'
    )
    creator.add_argument(
        '-d', '--source_dir', dest='PROJECT_SOURCE',
        type=str,
        help=(
            'Directory where the project files reside. These files should '
            'include the ones for which documenation will be generated.'
        ),
        default='.'
    )

    # NOTE the destination is SOURCE_DIR below, that is for the tempaltes
    creator.add_argument(
        '-s', '--install_dir', dest='SOURCE_DIR',
        type=str,
        help=(
            'Installation directory for the artifacts. This will be the site '
            'where project documentation is generated.'
        ),
        default='.'
    )
    creator.add_argument(
        '-b', '--build_dir', dest='BUILD_DIR',
        type=str,
        help=(
            'Directory where the documentation will be built. The value '
            'should be relative to SOURCE_DIR.'
        ),
        default='docs'
    )
    creator.add_argument(
        '--extensions', dest='EXTENSIONS',
        nargs='+',
        help=(
            'Add any Sphinx extension module names here, as strings. '
            'These can be sphinx generated or custom extensions.'
        ),
        default=['sphinx.ext.autodoc', 'sphinx.ext.autosummary']
    )
    creator.add_argument(
        '--templates', dest='TEMPLATES',
        nargs='+',
        help=(
            'Paths that contain templates, these should be relative to '
            'the SOURCE_DIR.'
        ),
        default=[]
    )
    creator.add_argument(
        '--exclusions', dest='EXCLUSIONS',
        nargs='+',
        help=(
            'List of patterns, relative to SOURCE_DIR, that match files '
            'and directories to ignore when looking for source files.'
        ),
        default=[]
    )
    creator.add_argument(
        '--static', dest='STATIC_PATHS',
        nargs='+',
        help=(
            'Add any paths that contain custom static files (such as style '
            'sheets), relative to SOURCE_DIR.'
        ),
        default=[]
    )
    creator.add_argument(
        '--hide_artifacts',
        help=(
            'When present, the artifacts file will be hidden in '
            'the SOURCE_DIR.'
        ),
        action='store_true'
    )

    args = parser.parse_args()
    create_logger(args)
    globals()[args.command](args)

    
def create_logger(args):
    """Initialize the logger."""
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


def create(args):
    """Execute the create functionality to document the 
    project and create the artifacts.
    """
    log.info("Generating templates")
    main_templates = generate_sphinx(**vars(args))
    log.debug("Created the following files from templates: \n\t{}".format(
              "\n\t".join(main_templates)))
    
    artifacts = {}
    for temp in main_templates:
        artifacts[temp] = False

    log.info("Source Directory set to {}".format(args.PROJECT_SOURCE))
    src_tree = generate_tree(directory=args.PROJECT_SOURCE, exclusions=args.EXCLUSIONS)
    rst_artifacts = generate_rst(src_tree, "{}/rst_docs".format(
        args.SOURCE_DIR))
    artifacts.update(rst_artifacts)
    artifacts.update(generate_docs_dir(args.SOURCE_DIR, args.BUILD_DIR))

    log_artifacts(
        args.SOURCE_DIR, artifacts=artifacts, hide_file=args.hide_artifacts)

    log.info("Executing sphinx")
    log.debug("Attempting to make on {} ...".format(platform))
    
    if platform.lower() in ("win32", "cygwin"):
        log.debug("  Windows system ...")
        if exists("{}/make.bat".format(args.SOURCE_DIR)):
            system("cd {} && make.bat html && cd -".format(args.SOURCE_DIR))
        else:
            log.error("No make.bat found in {}".format(args.SOURCE_DIR))
    else:
        if exists("{}/Makefile".format(args.SOURCE_DIR)):
            system("cd {} && make html && cd -".format(args.SOURCE_DIR))
        else:
            log.error("No Makefile found in {}".format(args.SOURCE_DIR))


def clean(args):
    """Execute the cleanup of all artifacts."""


    log.debug("Attempting to make clean on {} ...".format(platform))
    if platform.lower() in ("win32", "cygwin"):
        log.debug("  Windows system ...")
        if exists("{}/make.bat".format(args.SOURCE_DIR)):
            system("cd {} && make.bat clean && cd -".format(args.SOURCE_DIR))
        else:
            log.error("No make.bat found in {}".format(args.SOURCE_DIR))
    else:
        if exists("{}/Makefile".format(args.SOURCE_DIR)):
            system("cd {} && make clean && cd -".format(args.SOURCE_DIR))
        else:
            log.error("No Makefile found in {}".format(args.SOURCE_DIR))
    
    log.info("Cleaning artifacts ...")
    destroy(args.SOURCE_DIR)


if __name__ == "__main__":
    main()
