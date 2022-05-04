from logging import getLogger


log = getLogger()

ARTIFACTS_FILENAME = "autodoc_ext_artifacts.yaml"


def log_artifacts(source_dir, hide_file=True):
    """
    Create build process logs/artifacts that will be used for during the destruction/cleanup
    process. The name of the file will be `autodoc_ext_artifacts.yaml`.

    :param source_dir: Source directory where the artifaces file will reside.
    :param hide_file: When true [default], hide the artifacts file when created.
    """


def destroy(source_dir):
    """
    Read the artifacts file from the source directory. All of the artifacts that are logged in the
    file (known objects) will be destroyed. The labels in the file designated `keep` will be kept 
    as part of the destruction.
    
    :param source_dir: Source directory where the artifacts file will reside.
    
    :return: True when the data was successfully removed, false otherwise
    """
    return False
