from jinja2 import Template
from os.path import abspath, dirname, isfile, join
from os import listdir
from logging import getLogger
from .args import check_args
from os.path import exists
from os import makedirs


log = getLogger()


subPackageTemplate = \
'''Subpackages
-----------

.. toctree::
   :maxdepth: 4
  
   {{ SUBPACKAGES }}

'''

autoModuleTemplate = \
'''.. automodule:: {{ PACKAGE }}
   :members:
   :undoc-members:
   :show-inheritence:
'''

autoClassTemplate = \
'''.. {{ AUTOTYPE }}:: {{ PACKAGE }}::{{ CLASSNAME }}
   :members:
   :undoc-members:
   :private-members:
   :special-members:
   :inherited-members:
'''


def generate_sphinx(*args, **kwargs):
    """
    Find all .j2 extension files in this directory. Fill the template files
    with the parameters that were passed in to this function.
    Args:
      PROJECT                 (str): Name of the project that the documents
                                     are generated for.
      COPYRIGHT               (int): Year of the copyright for the `PROJECT`.
      AUTHOR                  (str): Author(s) of the `PROJECT` as a single
                                     string.
      VERSION                 (str): Version of the `PROJECT`.
      EXTENSIONS        (list[str]): Extension packages that can be combined
                                     with sphinx. Ex: rinoh.
      TEMPLATES         (list[str]): Path(s) containing templates.
      EXCLUSIONS   (list[str/path]): Path(s) and patterns of files to exclude
                                     from documentation.
      THEME                   (str): The theme to use for HTML and HTML Help
                                     pages.
      STATIC_PATHS (list[str/path]): Path(s) that contain custom static files.
      SOURCE_DIR         (str/path): Directory where the source of the
                                     software package is located.
      BUILD_DIR          (str/path): Directory where the sphinx build will
                                     occur.

    Artifacts:
      The following artifacts will be placed into the `SOURCE_DIR`

      Makefile: see `Makefile.j2`
      make.bat: see `make.bat.j2`
      conf.py:  see `conf.py.j2`


    Returns:
      List of files that were generated
    """
    args = check_args(kwargs)
    templates_path = join(dirname(abspath(__file__)), "templates/sphinx")
    j2files = {
      join(templates_path, f): f
      for f in listdir(templates_path)
      if isfile(join(templates_path, f)) and f.endswith(".j2")
    }
    source = args["SOURCE_DIR"]

    generated_files = []
    for full_file, j2file in j2files.items():

        log.info("Reading template {}".format(full_file))
        with open(full_file, "r") as jf:
            template = Template(jf.read())
            log.debug("Rendering template {}".format(full_file))
            output = template.render(**args)

        # write the files to the source directory where project
        # code should reside
        gen_file_name = join(source, j2file.replace(".j2", ""))
        log.info("Writing data to {}".format(gen_file_name))
        with open(gen_file_name, "w+") as ic:
            ic.write(output)
        generated_files.append(gen_file_name)

    return generated_files


def generate_modules_rst(package, directory):
  """_summary_

  Args:
      package (_type_): _description_
      directory (_type_): _description_
  """
  log.debug("Generating modules.rst")
  template_file = join(dirname(abspath(__file__)), 
                       "templates/rst/modules.rst.j2")
  
  log.info("Reading template {}".format(template_file))
  with open(template_file, "r") as j2file:
    template = Template(j2file.read())
    log.debug("Rendering template {}".format(template_file))
    output = template.render({"PACKAGE": package})
  
  generated_file = join(directory, "modules.rst")
  log.info("Writing data to {}".format(generated_file))
  with open(generated_file, "w+") as gen_file:
    gen_file.write(output)


def generate_rst(tree, directory="."):
    """Generate the rst files for the tree

    Args:
        tree (Node): Node class that is used to generate rst documents.
        directory (str, optional): Output directory for all rst documents.
        Defaults to ".".
    """
    def _generate_rst(t, d, templates, p=None):
        """Generate the rst files for the tree [inner function]

        Args:
            t (Node): Node class that is used to generate rst documents.
            d (str, optional): Output directory for all rst documents.
            Defaults to ".".
            templates (dict): dict of Jinja Templates
            p (str): Parent string for the current node. Defaults to None.
        """
        template_data = {"PACKAGE": p+"."+t.name if p is not None else t.name}
        subpackages = ["{}.{}".format(
          template_data["PACKAGE"], child.name) for child in t.children]
        if subpackages:
            template_data["SUBPACKAGE_DATA"] = templates["subs"].render(
              {"SUBPACKAGES": "\n   ".join(subpackages)}
            )

        contents = [templates["module"].render(template_data)]
        classes = t.classes
        if classes:
            for c in classes:
                auto_class_filler = {
                  "PACKAGE": template_data["PACKAGE"], 
                  "CLASSNAME": c,
                  "AUTOTYPE": "autoclass"
                }
                log.debug("Found class for the module: {}".format(c))
                # exceptions are a special case of classes
                if "error" in c.lower() or "exception" in c.lower():
                    auto_class_filler["AUTOTYPE"] = "autoexception"
                    log.debug("{} is an exception".format(c))

                contents.append(templates["class"].render(auto_class_filler))

        # fill the contents section with the templates created
        template_data["CONTENTS"] = "\n\n".join(contents)
        
        output = templates["rst"].render(template_data)
        rst_filename = join(directory, "{}.rst".format(template_data["PACKAGE"]))
        log.info("Generating {}".format(rst_filename))
        with open(rst_filename, "w+") as rst_file:
            rst_file.write(output)
        
        for child in t.children:
            _generate_rst(child, d, templates, p=template_data["PACKAGE"])

    # Dictionary that will contain all Templates so they do not need to be 
    # generated each time the inner function is called
    templates = {
      "module": Template(autoModuleTemplate),
      "class": Template(autoClassTemplate),
      "subs": Template(subPackageTemplate)
    }
    template_file = join(dirname(abspath(__file__)), "templates/rst/rst.j2")
    log.info("Reading template {}".format(template_file))
    with open(template_file, "r") as j2file:
      templates["rst"] = Template(j2file.read())
      
    log.info("Generating rst files in {}".format(directory))
    if not exists(directory):
        log.info("Creating directory {}".format(directory))
        makedirs(directory)

    generate_modules_rst(tree.name, directory=directory)
    _generate_rst(tree, directory, templates)