import argparse
import logging


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
    parser = argparse.ArgumentParser(description='Automatically create the rst files for documentation with Sphinx.')
    parser.add_argument('-v', '--verbose', action='count', default=0, help='Verbosity level for logging')
    args = parser.parse_args()

    # verbosity starts at 10 and moves to 50
    verbosity = 50 - (10*(args.verbose-1)) if args.verbose > 0 else logging.CRITICAL

    # Create the logger. Use the default name for every log that will operate
    # during the use of this application.
    log = logging.getLogger()
    log.setLevel(verbosity)

    # Add a formatter to color the log output and format the text
    handler = logging.StreamHandler()
    handler.setFormatter(LogColorFormatter())
    log.addHandler(handler)

    
if __name__ == "__main__":
    main()
