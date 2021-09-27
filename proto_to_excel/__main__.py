import argparse
from xlwt import Workbook, XFStyle
from enum import Enum
import json
import importlib


class DynamicMessageImporter:

    def __init__(self, channel_type_alias_map={}):
        """
        :param channel_type_alias_map (default={}): Map aliasing message types to the channel.
            DynoImporter(
                channel_type_alias_map={"example.channel": "sas.example_msgs.ExampleMessage"}
            )
                This will allow the import from a received channel of "example.channel" to
                map to the message type "sas.example_msgs.ExampleMessage".
        """
        self.channel_msg_type_alias_map = channel_type_alias_map
        self.dynamically_imported_modules = {}        

    @staticmethod
    def module_components(full_name):
        """
        :param full_name:
        """
        split_msg_type = full_name.split('.')
        attr = split_msg_type.pop(len(split_msg_type)-1)
        module = '.'.join(split_msg_type)
        return module, attr

    def init_msg_combined(self, full_topic):
        """

        :param full_topic: full name of the message to import
        """
        module, topic = DynamicMessageImporter.module_components(full_topic)
        return self.init_msg_detailed(module, topic)

    def init_msg_detailed(self, module, topic, already_attempted=False):
        """
        Initialize the instance of the Message.

        Example:
           channel = "sas.example_msgs.ExampleMessage"
           module, topic = module_components(channel)
           imported_module = import_module(module)

               If successful, imported module would contain the module "sas.example_msgs"
        
           msg = init_msg(imported_module, topic)


        :param module: Module or channel that the message is received on. The module can be an indicator
        into the package.

        :param topic: Name of the message

        :param already_attempted: [default=False], When True, attempt to initialize the message under
        new criteria where the module can be found in the alias map.
        
        :return: The initialized message if one exists, None otherwise.
        """
        msg = None
        try:
            imported_mod = importlib.import_module(module)
            if hasattr(imported_mod, topic):
                msg = getattr(imported_mod, topic)()
            else:
                imported_mod = importlib.import_module(module+"."+topic)
                if hasattr(imported_mod, topic):
                    msg = getattr(imported_mod, topic)()
        except (ModuleNotFoundError, ImportError, ValueError) as e:
            if not already_attempted:
                channel = next((y for x, y in self.channel_msg_type_alias_map.items() if y == module), None)
                if channel is not None:
                    # Still using the original topic
                    msg = self.init_msg(self.channel_msg_type_alias_map[channel], topic, already_attempted=True)
        finally:
            return msg


class CPPFieldType(Enum):
    CPPTYPE_INT32 = 1
    CPPTYPE_INT64 = 2
    CPPTYPE_UINT32 = 3
    CPPTYPE_UINT64 = 4
    CPPTYPE_DOUBLE = 5
    CPPTYPE_FLOAT = 6
    CPPTYPE_BOOL = 7
    CPPTYPE_ENUM = 8
    CPPTYPE_STRING = 9
    CPPTYPE_MESSAGE = 10

    __str__ = lambda self: self.name.replace("CPPTYPE_", "").lower().capitalize()

    
class PyFieldType(Enum):
    TYPE_DOUBLE = 1
    TYPE_FLOAT = 2
    TYPE_INT64 = 3
    TYPE_UINT64 = 4
    TYPE_INT32 = 5
    TYPE_FIXED64 = 6
    TYPE_FIXED32 = 7
    TYPE_BOOL = 8
    TYPE_STRING = 9
    TYPE_GROUP = 10
    TYPE_MESSAGE = 11
    TYPE_BYTES = 12
    TYPE_UINT32 = 13
    TYPE_ENUM = 14
    TYPE_SFIXED32 = 15
    TYPE_SFIXED64 = 16
    TYPE_SINT32 = 17
    TYPE_SINT64 = 18

    __str__ = lambda self: self.name.replace("TYPE_", "").lower().capitalize()


class FieldLabel(Enum):
    LABEL_OPTIONAL = 1
    LABEL_REQUIRED = 2
    LABEL_REPEATED = 3

    __str__ = lambda self: self.name.replace("LABEL_", "").lower().capitalize()


# predefined Header information.
# FUTURE USE: add ability to state headers
MESSAGE_COL = 0
FIELD_COL = 1
FIELD_TYPE_COL = 2
DESC_COL = 3
DEFAULT_COL = 4


def document_all(message_map, excel_file_name="test.xls", error_file_name="error.json"):
    """
    :param message_map
    """
    wb = Workbook()

    importer = DynamicMessageImporter()
    
    error_dir = {}
    imported_msgs = {}

    for key, message_list in message_map.items():

        error_dir[key] = []
        imported_msgs[key] = []

        for full_msg_name in message_list:
            module, attr = DynamicMessageImporter.module_components(full_msg_name)
            msg = importer.init_msg_detailed(module, attr)
            if msg is None:
                error_dir[key].append(full_msg_name)
            else:
                imported_msgs[key].append(msg)
    
    for data in imported_msgs:
        if imported_msgs[data]:
            _document(wb, data, imported_msgs[data])
   
    with open(error_file_name, "w") as errorData:
        errorData.write(json.dumps(error_dir, indent=4))
    
    wb.save(excel_file_name)


def _document(wb, sheet_name, msgs):
    """
    :param wb: Workbook where the sheets will be added
    :param sheet_name: Name of the sheet that will appear in the excel document
    :param msgs: all of the imported messages for this sheet.
    """

    datasheet = wb.add_sheet(sheet_name)

    # it's probably ok just keep recreating this one.
    style = XFStyle()
    style.alignment.wrap = 1

    # headers
    datasheet.write(0, MESSAGE_COL, "Message Type")
    datasheet.write(0, FIELD_COL, "Field Name")
    datasheet.write(0, FIELD_TYPE_COL, "Field Type")
    datasheet.write(0, DESC_COL, "Description")
    datasheet.write(0, DEFAULT_COL, "Default Value")

    curr_row = 1


    for msg in msgs:
        if hasattr(msg, "DESCRIPTOR"):
            if curr_row > 0:
                curr_row = curr_row + 1

            datasheet.write(curr_row, MESSAGE_COL, msg.DESCRIPTOR.name, style)
            curr_row = curr_row+1
            
            for field_number, field in msg.DESCRIPTOR.fields_by_number.items():
                datasheet.write(curr_row, FIELD_COL, field.name, style)

                if field.type == PyFieldType.TYPE_MESSAGE.value:
                    type_str = field.message_type.name
                else:
                    type_str = str(PyFieldType(field.type))

                if field.label == FieldLabel.LABEL_REPEATED:
                    type_str = type_str + " (repeated)"
            
                datasheet.write(curr_row, FIELD_TYPE_COL, type_str, style)

                if field.type == PyFieldType.TYPE_ENUM.value:
                    e_str = "{}\n\n".format(field.enum_type.name)
                    for ev, en in field.enum_type.values_by_number.items():
                        e_str = e_str + "{}={}\n".format(en.name, ev)
                
                    datasheet.write(curr_row, DESC_COL, e_str, style)

                if field.has_default_value:
                    if field.type == PyFieldType.TYPE_ENUM.value:
                        datasheet.write(curr_row, DEFAULT_COL, field.enum_type.values_by_number[
                            field.default_value].name, style
                        )
                    else:
                        datasheet.write(curr_row, DEFAULT_COL, field.default_value, style)

                curr_row = curr_row + 1


def main():
    """
    Main Entry Point
    """
    parser = argparse.ArgumentParser(description='Simple Server to pass data between connections.')
    parser.add_argument('config_file', type=str, help='JSON Configuration file that states how to output the data')
    parser.add_argument('--excel_file', type=str, help='Filename for the excel data to be output to.', default='test.xls')
    parser.add_argument('--error_file', type=str, help='JSON file documenting errors', default='error.json')
    args = parser.parse_args()
    
    with open(args.config_file, "r") as jsonConfigFile:
        jsonData = json.load(jsonConfigFile)

    document_all(jsonData, args.excel_file, args.error_file)


if __name__ == '__main__':
    main()

