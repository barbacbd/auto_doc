from logging import getLogger
from os.path import join
from yaml import dump, safe_load
from os.path import exists, isdir
from shutil import rmtree
from os import remove


log = getLogger()

ARTIFACTS_FILENAME = "autodoc_ext_artifacts.yaml"


def log_artifacts(source_dir, artifacts, hide_file=True):
    """
    Create build process logs/artifacts that will be used for during the
    destruction/cleanup process. The name of the file will be
    `autodoc_ext_artifacts.yaml`.

    :param source_dir: Source directory where the artifaces file will reside.
    :param artifacts: Dictionary containing the artifacts that have been
    created and whether or not they should reside
    :param hide_file: When true [default], hide the artifacts file when
    created.
    """
    filename = "."+ARTIFACTS_FILENAME if hide_file else ARTIFACTS_FILENAME
    artifact_file = join(source_dir, filename)
    log.info("Creating artifacts file: {}".format(artifact_file))
    
    with open(artifact_file, 'w+') as yaml_artifacts:
        dump(artifacts, yaml_artifacts)


def destroy(source_dir):
    """
    Read the artifacts file from the source directory. All of the artifacts
    that are logged in the file (known objects) will be destroyed. The labels
    in the file designated `keep` will be kept as part of the destruction.

    :param source_dir: Source directory where the artifacts file will reside.

    :return: True when the data was successfully removed, false otherwise
    """

    filename = join(source_dir, ARTIFACTS_FILENAME)
    if not exists(filename):
        filename = join(source_dir, "."+ARTIFACTS_FILENAME)
        if not exists(filename):
            log.error(
                "Failed to find artifacts file in {}".format(source_dir))
            return
    
    with open(filename, "r") as yaml_file:
        artifacts = safe_load(yaml_file)
    
    for fname, keep in artifacts.items():
        if not exists(fname):
            log.warning("Could not find: {}, skipping ...".format(fname))
            continue
        
        if isdir(fname) and not keep:
            log.debug("Removing dir {}".format(fname))
            rmtree(fname)
        elif not keep:
            log.debug("Removing file {}".format(fname))
            remove(fname)
        else:
            log.info("Keeping {}".format(fname))
    
    log.debug("Removing artifact file ...")
    if exists(filename):
        remove(filename)

