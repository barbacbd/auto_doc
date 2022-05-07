from autodoc_ext.artifacts import log_artifacts, destroy, ARTIFACTS_FILENAME
from pathlib import Path
from os import makedirs
from os.path import exists, isfile


def test_create_artifacts():
    '''Create a simple set of artifacts'''
    makedirs("artifacts")
    p1 = Path("artifacts/test1.rst").touch()
    p2 = Path("simple_artifact.html").touch()
    
    artifacts = {
        "artifacts/test1.rst": False,
        "artifacts": False,
        "simple_artifact.html": False
    }
    
    log_artifacts(".", artifacts, False)
    
    assert exists(ARTIFACTS_FILENAME)
    assert isfile(ARTIFACTS_FILENAME)


def test_create_artifacts_hidden():
    '''Create a simple set of artifacts (hidden)'''
    makedirs("artifacts_hidden")
    p1 = Path("artifacts_hidden/test1.rst").touch()
    p2 = Path("simple_artifact_hidden.html").touch()
    
    artifacts = {
        "artifacts_hidden/test1.rst": False,
        "artifacts_hidden": False,
        "simple_artifact_hidden.html": False
    }
    
    log_artifacts(".", artifacts, True)
    
    assert exists("."+ARTIFACTS_FILENAME)
    assert isfile("."+ARTIFACTS_FILENAME)


def test_destroy_artifacts():
    '''Destroy the base artifacts file'''
    destroy(".")
    assert not exists(ARTIFACTS_FILENAME)


def test_destroy_artifacts_hidden():
    '''Destroy the base artifacts hidden file'''
    destroy(".")
    assert not exists("."+ARTIFACTS_FILENAME)