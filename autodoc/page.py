class Page:

    """
    A Page object represents all of the data that will be contained in a single rst file that is
    used to create a documentation page with the Sphinx tool.
    """

    def __init__(
            self,
            display_name: str,
            path_to_content: str,
            content=None,
            children=None
    ):
        """
        :param display_name: The name that will be displayed at the top of the web page
        :param path_to_content:
        :param content: list of strings containing data relavent to this module.
        :param children: list of pages that are considered children to this page
        """

        self._display_name = display_name
        self._mod_name = path_to_content.replace("\\", "/").replace("/", ".")

        # surprisingly enough, replace.replace is efficient /laughing !
        self._link = path_to_content.replace("\\", "/").replace("/", "_")
        # the page that we are creating is rst file, so the filename will always end with .rst
        self._filename = self._link + ".rst"

        self._content = []
        self._children = []

        # use the protected functions
        self.content = content
        self.children = children

    @property
    def filename(self):
        """
        :return: Full filename of the rst file that will be saved and contain the content for this page.
        """
        return self._filename

    @property
    def link(self):
        """
        :return: rst link (<example>) to the actual file containing the data for this page.
        """
        return self._link

    @property
    def display_name(self):
        """
        :return: The name that will be displayed at the top of the web page and the name that will be used
        as links when this page is a child of another
        """
        return self._display_name

    @property
    def children(self):
        """
        :return: List of children that are also Page objects
        """
        return self._children

    @children.setter
    def children(self, c):
        """
        Set the children for this page.

        :param c: If this is a list, only the items that are Page objects will be added. If this parameter is a
        Page object it will be added to the list.

        .. note::
            The list is reset each time this function is called/accessed.
        """
        if isinstance(c, list):
            self._children = [x for x in c if isinstance(x, Page)]
        elif isinstance(c, Page):
            self._children = [c]

    @property
    def content(self):
        """
        :return: list of filenames that are a part of the directory that will be used to create this page
        """
        return self._content

    @content.setter
    def content(self, c):
        """
        Set the content (files) that are contained on this page. The content could be files or functions from
        several files.

        :param c: If this is a list, only the string items will be added. If this parameter is a string it will be
        added to the list.

        .. note::
            The list is reset each time this function is called/accessed.
        """
        if isinstance(c, list):
            self._content = [x for x in c if isinstance(x, str)]
        elif isinstance(c, str):
            self._content = [c]

    @classmethod
    def special_content(cls):
        """
        Place all files considered special content here. These files are considered header and special
        cases and should NOT have sub-pages (link) or sub-sections.

        :return: List of file names that are considered special cases
        """
        return [
            "__init__.py"
        ]

    @property
    def data(self):
        """
        The data property contains all of the data that should be output to a file exactly as it should be written.

        :return: The string data that will be used to create a rst file.
        """
        # Header information
        _hdr = "=" * (len(self._display_name) + 1)
        output = f"{_hdr}\n{self._display_name}\n{_hdr}\n"
        # TOC information
        output += ".. toctree::\n   :maxdepth: 2\n\n"

        for c in self._children:
            output += f"   {c.display_name} <{c.link}>\n"

        output += "\n"

        # only the fisrt special content will be taken as the header information
        for c in self._content:
            if c in Page.special_content():
                name_split = c.split(".")
                if name_split:
                    output += f".. automodule:: {self._mod_name}.{name_split[0]}\n"
                    output += "   :members:\n   :special-members:\n\n"

        for c in self._content:
            if c not in Page.special_content():
                name_split = c.split(".")
                if name_split:
                    _frame = "-" * (len(name_split[0]) + 1)
                    output += f"{name_split[0]}\n{_frame}\n"
                    output += f".. automodule:: {self._mod_name}.{name_split[0]}\n"
                    output += "   :members:\n   :special-members:\n\n"

        return output
