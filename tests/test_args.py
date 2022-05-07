import pytest
from autodoc_ext.args import simple_arg_format, list_arg_format, check_args
from datetime import datetime


def test_simple_str_valid():
    '''Test a simple string arg, default does NOT matter'''
    assert simple_arg_format("safasdf", str, 123) == "safasdf"

    
def test_simple_str_invalid():
    '''Test a simple string arg, default Matters, string is invalid'''
    assert simple_arg_format(123, str, "safasdf") == "safasdf"

    
def test_simple_int_valid():
    '''Test a simple int arg, default does NOT matter'''
    assert simple_arg_format(12, int, "12312") == 12

    
def test_simple_int_invalid():
    '''Test a simple int arg, default Matters, int is invalid'''
    assert simple_arg_format("12312", int, 12) == 12

    
def test_simple_float_valid():
    '''Test a simple float arg, default does NOT matter'''
    assert simple_arg_format(123.23, float, "asfdsfA") == 123.23

    
def test_simple_float_invalid():
    '''Test a simple float arg, default Matters, float is invalid'''
    assert simple_arg_format("132123", float, 123.23) == 123.23

    
def test_simple_bool_valid():
    '''Test a simple bool arg, default does NOT matter'''
    assert simple_arg_format(True, bool, False) == True

    
def test_simple_bool_invalid():
    '''Test a simple bool arg, default Matters, bool is invalid'''
    assert simple_arg_format("sfasdf", bool, False) == False

    
def test_list_all_valid():
    '''Test that a list has all of the same values in it as before'''
    prelist = ["abc", 123, 432.23423, "234234"]
    types = (str, int, float)
    result = list_arg_format(prelist, types)
    
    final_result = True
    for value in prelist:
        if isinstance(value, types):
            final_result &= value in result

    assert final_result

    
def test_list_some_valid():
    '''Test that a list has some of the same values in it as before'''
    prelist = ["abc", 123, 432.23423, "234234"]
    types = (str, float)
    result = list_arg_format(prelist, types)
    
    final_result = True
    for value in prelist:
        if isinstance(value, types):
            final_result &= value in result

    assert final_result

    
def test_list_none_valid():
    '''Test that a list has none of the same values in it as before'''
    prelist = ["abc", 123, 432.23423, "234234"]
    result = list_arg_format(prelist, bool)
    assert len(result) == 0


def test_all_defaults():
    '''Test receiving all default values'''
    results = check_args()
    
    assert results["PROJECT"] == ""
    assert results["COPYRIGHT"] == datetime.now().year
    assert results["AUTHOR"] == ""
    assert results["VERSION"] == "0.0.0"
    assert len(results["EXTENSIONS"]) > 0
    assert results["TEMPLATES"] == []
    assert results["EXCLUSIONS"] == []
    assert results["THEME"] == ""
    assert results["STATIC_PATHS"] == []
    assert results["SOURCE_DIR"] == "."
    assert results["BUILD_DIR"] == "docs"
    

def test_all_set_no_defaults():
    '''Set all of the values through kwargs, make sure all set correctly'''
    predata = {
        "PROJECT": "TEST",
        "COPYRIGHT": datetime.now().year-1,
        "AUTHOR":  ["ME"],
        "VERSION": "1.0.0",
        "EXTENSIONS": ["TEST_EXT"],
        "TEMPLATES": ["TEST_TEMPLATES"],
        "EXCLUSIONS": ["EXCLUDED_FILES"],
        "THEME": "TEST THEME",
        "STATIC_PATHS": ["_STATIC"],
        "SOURCE_DIR": "src",
        "BUILD_DIR": "build"
    }
    
    results = check_args(**predata)

    for k, v in results.items():
        if k == "AUTHOR":
            assert v == predata[k][0]
        else:
            assert v == predata[k]

def test_values_set_incorrect_names():
    '''the values with incorrect names/keys will not be set correctly'''
    predata = {
        "project": "TEST",
        "COPYRIGHT": datetime.now().year-1,
        "author":  "ME",
        "VERSION": "1.0.0",
        "EXTENSIONS": ["TEST_EXT"],
        "TEMPLATES": ["TEST_TEMPLATES"],
        "EXCLUSIONS": ["EXCLUDED_FILES"],
        "theme": "TEST THEME",
        "STATIC_PATHS": ["_STATIC"],
        "SOURCE_DIR": "src",
        "bd": "build"
    }
    
    results = check_args(**predata)
    default_results = check_args()

    expected_default_fields = set(list(default_results.keys())).difference(set(list(predata.keys())))    
    actual_default_fields= []
    for k, v in results.items():
        if k in predata:
            assert v == predata[k]
        else:
            actual_default_fields.append(k)

    defaults_match = len(expected_default_fields) == len(actual_default_fields)
    if defaults_match:
        for k in expected_default_fields:
            defaults_match &= (k in actual_default_fields)
    assert defaults_match
            
