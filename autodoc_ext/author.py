from autodoc.page import Page
from threading import Lock
from os import listdir, mkdir
from os.path import join, isdir, isfile, exists


class Author:

    """
    The author is the owner or CREATOR of pages.
    """
    def __init__(self, list_of_known_extensions):
        """
        :param list_of_known_extensions: list of strings containing extensions to look for
        when creating pages.
        """
        self._known_extensions = list_of_known_extensions if isinstance(list_of_known_extensions, list) else []
        self.lock = Lock()

    @property
    def extensions(self):
        """
        :return: known extensions
        """
        return self._known_extensions.copy()

    @extensions.setter
    def extensions(self, item):
        """
        :param item: list of strings to reset as the known extensions

        ..note::
            The list is replaced not appended or extended
        """
        with self.lock:
            if isinstance(item, list):
                _ext = [x for x in item if isinstance(x, str)]

                if _ext:
                    self._known_extensions = _ext

    def create_page(self, root, excluded_dirs, excluded_files):
        """

        :param root:
        :param excluded_dirs:
        :param excluded_files:
        :return:
        """

        _d = root.replace("\\", "/")
        _d_split = [x for x in _d.split("/") if x]

        return Author.create_page_static(
            root,
            excluded_dirs,
            excluded_files,
            self._known_extensions
        ) if len(_d_split) == 1 else None

    @staticmethod
    def create_page_static(root, excluded_dirs, excluded_files, known_extensions):
        """
        Generate a page tree that starts at the root directory. Each directory in the tree starting at root
        will have a Page object created for it.

        :param root: Root directory to create the Page object for.
        :param excluded_dirs: [list of directories that will not be searched [if found]
        :param excluded_files: list of files that should be excluded [if found]
        :param known_extensions: list of known extensions to find
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
                if True in [x.endswith(y) for y in known_extensions]:
                    _files.append(x)

        page.content = _files
        page.children = [
            Author.create_page_static(
                join(root, d),
                excluded_dirs,
                excluded_files,
                known_extensions
            ) for d in _dirs
        ]

        return page

    @staticmethod
    def generate_rst_tree(p: Page, save_dir: str = "rst_files", **kwargs):
        """
        Generate all rst files that correspond to the Page.

        :param p: Root page used to generate all of the rst files.
        :param save_dir: directory to save the files to after they are generated
        """
        _initialized = kwargs.get("initialized", True)

        if not _initialized:
            if not exists(save_dir):
                mkdir(save_dir)
            else:
                if not isdir(save_dir):
                    return

        with open(join(save_dir, p.filename), "w") as file:
            file.write(p.data)

        [
            Author.generate_rst_tree(
                p=c,
                save_dir=save_dir,
                initialized=True
            ) for c in p.children
        ]
