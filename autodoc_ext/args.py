from logging import getLogger
from datetime import datetime


log = getLogger()


def simple_arg_format(value, expected_types, default):
    """
    Check that the value is of an expected type. If it is not, use the
    default value:

    Args:
      value: Value to be checked
      expected_types (tuple): tuple of types to be used for verification
      default: default value to be set in the event that value is not of
               expected_types.

    Returns:
      type: value if matching expected types otherwise default
    """
    log.debug("simple_arg_format: {} - {} - {}".format(
      value, expected_types, default
    ))

    if isinstance(value, expected_types):
        log.debug("{} matches type(s) {}".format(value, expected_types))
        return value
    log.warning("{} did not match {}, returning {}".format(
      value, expected_types, default
    ))
    return default


def list_arg_format(list_of_values, expected_types):
    """
    Check that each value in `list_of_values` matches the expected_types. If
    the list of values is a primitive or simple type, it will be wrapped in
    a list and returned.

    Args:
      list_of_values: List (or primitive type) where the values will be
      checked. When the values are of the expected type, they are added to a
      returned list.

      expected_types (tuple): tuple of types to be used for verification

    Returns:
      list: All values that matched the expected_types will be added to the
      returned list.
    """
    log.debug("list_arg_format: {} - {}".format(
      list_of_values, expected_types
    ))
    if isinstance(list_of_values, (int, float, str, bool)):
        log.warning(
          "{} is a primitive type, sending to simple_arg_format".format(
            list_of_values
          ))
        simple_output = simple_arg_format(
          list_of_values, expected_types, None
        )     
        if simple_output is not None:
            return [simple_output]

        return []

    fl = []
    for v in list_of_values:
        simple_output = simple_arg_format(v, expected_types, None)
        if simple_output is not None:
            fl.append(simple_output)

    return fl


def check_args(*args, **kwargs):
    """
    Check the arguments to ensure that the following parameters are passed and
    contain the correct type. If the type is not correctly formatted and can
    be formatted it will be altered, otherwise the data is reset to a proper
    empty value.

    Args (expected):
      PROJECT                 (str): Name of the project that the documents
                                     are generated for.
      COPYRIGHT               (int): Year of the copyright for the `PROJECT`.
      AUTHOR                  (str): Author(s) of the `PROJECT` as a single
                                     string.
      VERSION                 (str): Version of the `PROJECT`.
      EXTENSIONS        (list[str]): Extenion packages that can be combined
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

    Returns:
      dict: dictionary formatted with the arguments above, if they did not
            exist in `kwargs`, defaults will be applied.
    """
    
    extensions = list_arg_format(kwargs.get(
      "EXTENSIONS", ['sphinx.ext.autodoc']), str)
    templates = list_arg_format(kwargs.get("TEMPLATES", ""), str)
    exclusions = list_arg_format(kwargs.get("EXCLUSIONS", ""), str)
    static_paths = list_arg_format(kwargs.get("STATIC_PATHS", ""), str)

    return {
        "PROJECT": simple_arg_format(kwargs.get("PROJECT", ""), str, ""),
        "COPYRIGHT": simple_arg_format(kwargs.get(
          "COPYRIGHT", datetime.now().year), (int, str), datetime.now().year),
        "AUTHOR": simple_arg_format(
          ",".join(kwargs.get("AUTHOR", "")), str, ""),
        "VERSION": simple_arg_format(
          kwargs.get("VERSION", "0.0.0"), str, "0.0.0"),
        "EXTENSIONS": extensions,
        "TEMPLATES": templates,
        "EXCLUSIONS": exclusions,
        "THEME": simple_arg_format(kwargs.get("THEME", ""), str, ""),
        "STATIC_PATHS": static_paths,
        "SOURCE_DIR": simple_arg_format(
          kwargs.get("SOURCE_DIR", "."), str, "."),
        "BUILD_DIR": simple_arg_format(
          kwargs.get("BUILD_DIR", "docs"), str, "docs")
    }
