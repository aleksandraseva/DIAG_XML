import os
import xml.etree.ElementTree as ET


def parse_path(path_string):
    """
    Pretvara '/unit-16/port-2' u ('unit-16', 'port-2')
    """
    parts = path_string.strip('/').split('/')
    if len(parts) != 2:
        raise ValueError(f"Nevažeći format putanje: {path_string}")
    return parts[0], parts[1]


def find_element_in_xml(xml_path, element_name):
    """
    Otvara XML i traži element sa tagom == element_name ili atributom name=element_name
    """
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        for elem in root.iter():
            if elem.tag == element_name or elem.attrib.get("name") == element_name:
                return elem
        return None
    except ET.ParseError:
        print(f"Greška u parsiranju: {xml_path}")
        return None


def search_in_all_folders(base_dir, path_string):
    """
    Prolazi kroz sve foldere unutar base_dir i traži podudaranje s path_string
    """
    unit_name, port_name = parse_path(path_string)
    target_filename = f"{unit_name}.xml"

    found_in_folders = []

    for folder_name in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder_name)
        if not os.path.isdir(folder_path):
            continue

        xml_path = os.path.join(folder_path, target_filename)
        if os.path.exists(xml_path):
            element = find_element_in_xml(xml_path, port_name)
            if element is not None:
                print(f"✅ Nađeno u folderu: {folder_name}")
                found_in_folders.append(folder_name)
            else:
                print(f"⚠️  Nema elementa '{port_name}' u: {xml_path}")
        else:
            print(f"❌ Nema fajla: {target_filename} u folderu: {folder_name}")

    return found_in_folders
