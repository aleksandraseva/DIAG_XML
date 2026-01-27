import xml.etree.cElementTree as ET
import re
import os


def get_card_type(config_xml):
    try:
        tree = ET.parse(config_xml)
        root = tree.getroot()
        element = None
        element = root.find("./MOB_CFG_AP")
        motype = element.attrib.get("motype", "")
        return motype.split(".")[1]
    except Exception as e:
        print(e)


def get_unit(config_xml):
    try:
        tree = ET.parse(config_xml)
        root = tree.getroot()
        unit = root.attrib.get("name", "")
        return unit
    except Exception as e:
        print(e)


def get_port_name(element):
    try:
        port_name = element.attrib.get("name", "")
        return port_name
    except Exception as e:
        print(e)


def get_chan(chan):
    try:
        chan_name = chan.attrib.get("name", "")
        return chan_name
    except Exception as e:
        print(e)


def get_parts_conf(conf_element):
    parts=[]
    try:
        element = None
        for element in conf_element.findall(".//MOB_CFG_AP"):
            if element is not None:
                name = element.get("name")
                if name.startswith("part-"):
                    parts.append(element)
        return parts
    except Exception as e:
        print(e)


def get_part_name(part):
    try:
        part_name = part.attrib.get("name", "")
        return part_name
    except Exception as e:
        print(e)


def get_role(part):
    try:
        element = None
        for element in part.findall(".//MOB_CFG_DB[@name='general']"):
            if element is not None:
                role_tag = element.find(".//role")
                if role_tag is not None:
                    return role_tag.text
    except Exception as e:
        print(e)


def find_port_by_label(config_xml, label):
    try:
        tree = ET.parse(config_xml)
        root = tree.getroot()
        element = None
        for element in root.findall("./MOB_CFG_AP/MOB_CFG_AP"):
            if "port" in element.attrib.get("name", ""):
                main_tag = element.find("./MOB_CFG_MD[@name='main']")
                if main_tag is not None:
                    labels_tag = main_tag.find("./MOB_CFG_DB[@name='labels']")
                    if labels_tag is not None:
                        uselLabel_tag = labels_tag.find(".//UserLabel")
                        if uselLabel_tag is not None:
                            if uselLabel_tag.text is not None:
                                if label in uselLabel_tag.text:
                                    return element
    except Exception as e:
        print(e)


def find_config_label(root_path, label):
    config_paths = []
    try:
        folders = os.listdir(root_path)
        for folder in folders:
            path = os.path.join(root_path, folder)
            for root, dirs, files in os.walk(path):
                if "common_config.xml" in files:
                    xml_path = os.path.join(root, "common_config.xml")
                    port = find_port_by_label(xml_path, label)
                    if port is not None:
                        config_paths.append(xml_path)
        return config_paths
    except Exception as e:
        print(e)


def find_locations_label(root_path, label):
    locations = []
    try:
        folders = os.listdir(root_path)
        for folder in folders:
            path = os.path.join(root_path, folder)
            for root, dirs, files in os.walk(path):
                if "common_config.xml" in files:
                    xml_path = os.path.join(root, "common_config.xml")
                    port = find_port_by_label(xml_path, label)
                    if port is not None:
                        locations.append(folder)
        return locations
    except Exception as e:
        print(e)


def is_seli_port(port_element):
    try:
        element = None
        for element in port_element.findall(f".//MOB_CFG_AP[@name]"):
            if element is not None:
                name = element.get("name")
                if name.startswith("chan-"):
                    return True
        return False
    except Exception as e:
        print(e)

def is_conf(element):
    try:
        element_name = element.attrib.get("name", "")
        if element_name.startswith("conf-"):
            return True
        return False
    except Exception as e:
        print(e)


def get_port(config_xml, port):
    try:
        tree = ET.parse(config_xml)
        root = tree.getroot()
        element = None
        for element in root.findall(f".//MOB_CFG_AP[@name='{port}']"):
            if element is not None:
                return element
    except Exception as e:
        print(e)


def get_chan_port(port_element, chan):
    try:
        element = None
        for element in port_element.findall(f".//MOB_CFG_AP[@name='{chan}']"):
            if element is not None:
                return element
    except Exception as e:
        print(e)


def get_seli_port(element):
    try:
        ports = []
        cfgm_tag = element.find("./MOB_CFG_MD[@name='cfgm']")
        if cfgm_tag is not None:
            for remote_tag in cfgm_tag.findall(".//remoteCtpDataList/remoteCtpData"):
                ctpRef = remote_tag.find("./ctpRef")
                ports.append(ctpRef.text)
        return ports
    except Exception as e:
        print(e)


def get_port_label(port_element):
    try:
        main_tag = port_element.find("./MOB_CFG_MD[@name='main']")
        if main_tag is not None:
            labels_tag = main_tag.find("./MOB_CFG_DB[@name='labels']")
            if labels_tag is not None:
                uselLabel_tag = labels_tag.find(".//UserLabel")
                if uselLabel_tag is not None:
                    return uselLabel_tag.text
    except Exception as e:
        print(e)


def get_port_freq(element):
    try:
        main_tag = element.find("./MOB_CFG_MD[@name='main']")
        if main_tag is not None:
            labels_tag = main_tag.find("./MOB_CFG_DB[@name='labels']")
            if labels_tag is not None:
                uselLabel_tag = labels_tag.find(".//UserLabel")
                if uselLabel_tag is not None:
                    return uselLabel_tag.text
    except Exception as e:
        print(e)


def get_ll_rr(label):
    try:
        pattern = r"(LL|RR)\s+\d+"
        res=re.search(pattern, label)
        if res is not None:
            text = re.search(pattern, label).group()
            if text:
                return re.sub(r"[- ]", "", text)
            else:
                return None
    except Exception as e:
        print(e)


if __name__ == "__main__":
    find_locations_label("konfiguracije", "RR40")


# for node in root.iter('MOB_CFG_AP'):
#     print(node.attrib)

# for node in root.findall("./MOB_CFG_AP/MOB_CFG_AP[@name='port-1']"):
#     for child in node.iter():
#         print(f"Tag: {child.tag}, Text: {child.text}")
