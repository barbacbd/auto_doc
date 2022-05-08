import os
from json import dumps
import ast
from logging import getLogger


log = getLogger()


class Node:
    """A node or leaf of an entire tree. The Node/leaf will contain
    the information located in a directory (including files, classes,
    subdirectories, path).
    """
    
    def __init__(self, name, path=None):
        """Initialize the instance of a Node

        :param name: Name of this node/leaf.
        :param path: path in the tree for this instance.
        Defaults to None.
        """
        self.name = name
        self.path = path
        self.parent = None
        self.children = []
        self.files = []

    @property
    def all_filenames(self):
        """Get all filenames (including path) contained in this instance

        :return: Instance files with path
        """
        return [os.path.join(self.path, f) for f in self.files]

    @property
    def public_filenames(self):
        """Get all filenames (including path) contained in this instance that
        are not prefaced with an underscore.

        :return: Instance files with path
        """
        return [os.path.join(self.path, f)
                for f in self.files if not f.startswith("_")]
    
    def project_files(self, filenames):
        """Get the project files without the extension.

        :param filenames: list of filenames in this instance.
        :return: Dictionary of full filename along with the formatted name.
        """
        return { filename:
           "{}.{}".format(
                self.parent,filename.split("/")[-1].replace(".py", "")
            ) for filename in filenames
        }

    @property
    def classes(self):
        """Get the list of classes found in the files of this instance

        :return: List of classes that were found in the files of this tree.
        """
        classes = []
        for longfile, shortfile in \
            self.project_files(self.all_filenames).items():

            with open(longfile, "r") as file_handle:
                file_data = ast.parse(file_handle.read())
                classes.extend(
                [
                    "{}::{}".format(shortfile, str(found_cls.name))
                    for found_cls in ast.walk(file_data)
                    if isinstance(found_cls, ast.ClassDef)
                ]
            )
        return classes

    @property
    def sphinx_name(self):
        """Name that will be used by sphinx docs

        :return: Formatted name for this node in the sphinx docs
        """
        return self.parent if self.parent else self.name
    
    @property
    def templates(self):
        """Create the unique set of template for this node so
        that that there are no duplicates when the rst files are
        generated. 

        :return: unique set of templates
        """
        templates = {}
        modules = list(self.project_files(self.public_filenames).values())
        if not modules:
            modules = list(self.project_files(self.all_filenames).values())
        classes = self.classes
        for m in modules:
            for c in classes.copy():
                if m in c:
                    log.debug("  Removing tempalate for {}".format(c))
                    classes.remove(c)

        return {
            "base": self.sphinx_name,
            "modules": modules,
            "classes": classes
        }
            
    @property
    def json(self):
        """JSON formatted dictionary object for this node

        :return: json formatted dictionary for this instance.
        """
        jsonDict = {self.name: {}}

        if self.path:
            jsonDict[self.name]['path'] = self.path

        if self.children:
            jsonDict[self.name]['children'] = []

        for child in self.children:
            jsonDict[self.name]['children'].append(child.json)
        jsonDict[self.name]['files'] = self.files

        classes = self.classes
        if classes:
            jsonDict[self.name]['classes'] = classes
        return jsonDict

    def __str__(self):
        """String override. See `json` for the format.

        :return: String representation of this instance
        """
        return dumps(self.json, indent=4)


def generate_tree(directory=".", parent=0, exclusions=[]):
    """Generate the tree by walking the directory structure and creating
    a node for each directory that has been found.

    :param directory: Directory where all files for the project will reside.
    :param parent: parent directory depth.
    :param exclusions: Exclude files/directories matching these names
    :return: A tree (Node) containing all information from the directory walk
    """
    log.info("Generating tree info for the directory {}".format(directory))
    # Find the base directory name (name of the base module)
    if directory == ".":
        full_dir = os.getcwd()
    else:
        full_dir = directory

    split_dir = full_dir.split("/")
    base_dir_name = split_dir[-1]
    log.debug("Setting base directory name to {}".format(base_dir_name))

    leaf = Node(base_dir_name, path=full_dir)
    leaf.parent = ".".join(split_dir[-(parent+1):])

    log.debug("  {} ...".format(full_dir))
    for filename in os.listdir(full_dir):

        log.debug("    {} ... ".format(filename))
        
        if filename.startswith("."):
            log.warning("Hidden file {}, skipping ...".format(filename))
            continue

        full_filename = os.path.join(full_dir, filename)
        if os.path.isfile(full_filename) and not filename.endswith(".py"):
            continue
        elif os.path.islink(full_filename):
            log.warning("  Found link: {}, skipping ...".format(filename))
            continue
        elif filename in exclusions:
            log.warning("  Found exclusion: {}, skipping ...".format(filename))
            continue

        log.debug(full_filename)
        if os.path.isdir(full_filename):
            log.debug("  Found directory".format(filename))
            leaf.children.append(generate_tree(
                full_filename, parent=parent+1, exclusions=exclusions))
        else:
            log.debug("  Found file: {}".format(filename))
            leaf.files.append(filename)
    return leaf
