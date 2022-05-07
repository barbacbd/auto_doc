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

        Args:
            name (str): Name of this node/leaf.
            path (str, optional): path in the tree for this instance. Defaults to None.
        """
        self.name = name
        self.path = path
        self.parent = None
        self.children = []
        self.files = []
    
    @property
    def classes(self):
        """Get the list of classes found in the files of this instance

        Returns:
            list: List of classes that were found in the files of this tree.
            This does NOT include the classes found in the children.
        """
        classes = []
        filenames = [os.path.join(self.path, f) for f in self.files]

        for filename in filenames:
            with open(filename, "r") as file_handle:
                file_data = ast.parse(file_handle.read())
                classes.extend(
                [
                    "{}.{}::{}".format(self.parent,filename.split("/")[-1].replace(".py", ""), str(found_cls.name))
                    for found_cls in ast.walk(file_data)
                    if isinstance(found_cls, ast.ClassDef)
                ]
            )
        return classes
    
    @property
    def json(self):
        """JSON formatted dictionary object for this node

        Returns:
            dict: Dictionary containing the children, filenames, path and
            classes that reside in the current tree node.
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

        Returns:
            str: String representation of this instance
        """
        return dumps(self.json, indent=4)


def generate_tree(directory=".", parent=0):
    """Generate the tree by walking the directory structure and creating
    a node for each directory that has been found.

    Args:
        directory (str, optional): Directory where all files for the
        project will reside. Generally this will only be the source
        directory for the code. Defaults to ".".
        parent: parent directory depth. Default to 0
    Returns:
        Node: A tree containing all information from the directory walk
    """
    log.info("Generating tree info for the directory {}".format(directory))
    # Find the base directory name (name of the base module)
    if directory == ".":
        full_dir = os.getcwd()
    else:
        full_dir = directory

    base_dir_name = full_dir.split("/")[-1]
    log.debug("Setting base directory name to {}".format(base_dir_name))

    leaf = Node(base_dir_name, path=full_dir)
    if parent == 0:
        leaf.parent = base_dir_name
    else:
        leaf.parent = ".".join(full_dir[-parent:])
    
    for filename in os.listdir(full_dir):

        if filename.startswith("."):
            log.warning("Hidden file {}, skipping ...".format(filename))
            continue
        
        if not filename.endswith(".py"):
            continue

        full_filename = os.path.join(full_dir, filename)
        if os.path.islink(full_filename):
            log.warning("  Found link: {}, skipping ...".format(filename))
            continue

        if os.path.isdir(full_filename):
            log.debug("  Found directory".format(filename))
            leaf.children.append(generate_tree(full_filename))
        else:
            log.debug("  Found file: {}".format(filename))
            leaf.files.append(filename)
    return leaf
