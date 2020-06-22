from os import listdir, mkdir, chdir
from os.path import join, isdir, isfile, exists
from autodoc.page import Page
from logging import getLogger


log = getLogger(__name__)


# known file extensions to use
_known_extensions = [
    ".py"
]


def create_page(root, excluded_dirs, excluded_files):
    """

    :param root:
    :param excluded_dirs:
    :param excluded_files:
    :return:
    """

    _d = root.replace("\\", "/")
    _d_split = [x for x in _d.split("/") if x]

    if 0 <= len(_d_split) > 1:
        log.error("Please run create_page from the base of the project.")
        return

    return _create_page(root, excluded_dirs, excluded_files)


def _create_page(root, excluded_dirs, excluded_files):
    """
    Generate a page tree that starts at the root directory. Each directory in the tree starting at root
    will have a Page object created for it.

    :param root: Root directory to create the Page object for.
    :param excluded_dirs: [list of directories that will not be searched [if found]
    :param excluded_files: list of files that should be excluded [if found]
    :return: Page object
    """

    _files = []
    _dirs = []

    _d = root.replace("\\", "/")
    _d_split = [x for x in _d.split("/") if x]
    display_name = _d_split[-1]

    page = Page(display_name, root)

    for x in listdir(root):

        _full = join(root, x)

        if isdir(_full) and x not in excluded_dirs:
            _dirs.append(x)

        elif isfile(_full) and x not in excluded_files:
            if True in [x.endswith(y) for y in _known_extensions]:
                _files.append(x)

    page.content = _files
    page.children = [_create_page(join(root, d), excluded_dirs, excluded_files) for d in _dirs]

    return page


def generate_rst_tree(p: Page, save_dir: str = "rst_files"):
    """
    Generate all rst files that correspond to the Page.

    :param p: Root page used to generate all of the rst files.
    :param save_dir: directory to save the files to after they are generated
    """

    if not exists(save_dir):
        log.warning(f"{save_dir} does not exist, creating ...")
        mkdir(save_dir)
    else:
        if not isdir(save_dir):
            log.error(f"{save_dir} is not a directory, will not create rst files.")
            return

    _generate_rst_tree(p, save_dir)


def _generate_rst_tree(p: Page, save_dir: str):
    """
    Internal function that will [recursively] generate all rst files for the page provided. The function will call
    itself to generate the files for all children in the Page Tree.

    :param p: Page whose rst file will be generated.
    :param save_dir: directory to save the file to after it is generated
    """
    with open(join(save_dir, p.filename), "w") as file:
        file.write(p.data)

    [_generate_rst_tree(c, save_dir) for c in p.children]
