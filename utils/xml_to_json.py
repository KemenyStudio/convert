import xmltodict
import json

def xml_to_json(xml_file):
    xml_content = xml_file.read()
    data_dict = xmltodict.parse(xml_content)
    return data_dict