import os
from enum import Enum
import gzip
import shutil
import XMLParser
import Diagram
import Node
import ConParser
import tkinter as tk
from tkinter import ttk, messagebox


class Locations_color(Enum):
    BLK1_SJJ = "orange"
    BLK2_KOZ = "purple"
    BLK3_PLV = "LightBlue"
    BLK_APP = "LightPink"
    BLK_GP = "gray"
    BTM = "LightGreen"
    BTM_APP = "aquamarine"
    BTM_RDR = "burlywood"
    BUK = "bisque"
    BUK_APP = "DarkOliveGreen3"
    JAH = "DarkSeaGreen"
    KOZ = "gold"
    MST = "lavender"
    PLV = "medium orchid"
    SJJ1_BLK = "thistle"
    SJJ2_JAH = "tomato"
    SJJ3_BUK = "YellowGreen"
    SJJ4_BTM = "dark khaki"
    TZL = "ghost white"
    UDR = "fuchsia"


class Location(Enum):
    BLK1_SJJ = "BLK 1 (SJJ)"
    BLK2_KOZ = "BLK 2 (KOZ)"
    BLK3_PLV = "BLK 3 (PLV)"
    BLK_APP = "BLK APP"
    BLK_GP = "BLK GP"
    BTM = "BTM"
    BTM_APP = "BTM APP"
    BTM_RDR = "BTM RDR"
    BUK = "BUK"
    BUK_APP = "BUK APP"
    JAH = "JAH"
    KOZ = "KOZ"
    MST = "MST"
    PLV = "PLV"
    SJJ1_BLK = "SJJ 1 (BLK)"
    SJJ2_JAH = "SJJ 2 (JAH)"
    SJJ3_BUK = "SJJ 3 (BUK)"
    SJJ4_BTM = "SJJ 4 (BTM)"
    TZL = "TZL"
    UDR = "UDR"


class GUI:
    def __init__(self, master, diag):
        self.diag = diag
        self.master = master

        master.title("")
        master.geometry("300x200")

        tk.Label(master, text="Frekvencija:").pack(pady=(10, 0))
        self.freq = tk.Entry(master)
        self.freq.pack(pady=5)

        tk.Label(master, text="Lokacija:").pack(pady=(10, 0))
        self.location = tk.StringVar(master)
        self.location.set(list(Location.__members__.keys())[0])

        self.dropdown = ttk.Combobox(
            master,
            textvariable=self.location,
            values=list(Location.__members__.keys()),
            state="readonly",
        )
        self.dropdown.pack(pady=5)

        tk.Button(master, text="Potvrdi", command=self.submit).pack(pady=15)

    def submit(self):

        self.diag.get_freq_loc(
            self.freq.get(), Location[self.location.get()].value, self.master
        )


class Diagram_XML:
    def __init__(self):
        self.diagram = Diagram.Diagram()
        self.conParser = ConParser.ConParser()
        self.colors = Locations_color
        self.root_folder = "konfiguracije"
        self.connections_file = "connections.txt"

    def get_freq_loc(self, freq, location, root):
        # try:
        self.unzip_all_common_config()
        self.find_config_freq(freq, location)
        self.diagram.diagram_draw(root)

    # except Exception as e:
    #     root = tk.Tk()
    #     root.withdraw()  # da se glavni prozor ne vidi
    #     messagebox.showerror("Greška", f"Došlo je do greške:\n{e}")
    #     root.destroy()

    # self.unzip_all_common_config()
    # self.find_config_freq(freq,location)
    # self.diagram.diagram_draw(root)

    def get_folders(self, location):
        folders = []
        if not os.path.exists(self.root_folder):
            print(f"Folder '{self.root_folder}' ne postoji.")
            return folders

        for folder in os.listdir(self.root_folder):
            path = os.path.join(self.root_folder, folder)
            if os.path.isdir(path) and folder.lower().replace(" ", "").replace(
                "_", ""
            ) == location.lower().replace(" ", "").replace("_", ""):
                folders.append(folder)
        return folders

    def unzip_all_common_config(self):
        folders = os.listdir(self.root_folder)
        for folder in folders:
            path = os.path.join(self.root_folder, folder)

            for root, dirs, files in os.walk(path):
                for file in files:
                    if file == "common_config.xml.gz":
                        gz_path = os.path.join(root, file)
                        xml_path = os.path.join(root, "common_config.xml")

                        if os.path.exists(xml_path):
                            continue

                        try:
                            with gzip.open(gz_path, "rb") as f_in:
                                with open(xml_path, "wb") as f_out:
                                    shutil.copyfileobj(f_in, f_out)
                            # print(f"Raspakovano: {gz_path} -> {xml_path}")
                        except Exception as e:
                            print(f"Greška prilikom raspakivanja {gz_path}: {e}")

    def find_config_freq(self, freq, location):
        # info_string = (self.get_freq_loc()).split("/")
        # config_dir = info_string[0]
        # freq = info_string[1]
        folders = self.get_folders(location)
        for folder in folders:
            path = os.path.join(self.root_folder, folder)
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file == "common_config.xml":
                        path_config_xml = os.path.join(root, file)
                        element = XMLParser.find_port_by_label(path_config_xml, freq)
                        if element is not None:
                            root_element = element
                            # location = config_dir.split()[0]
                            unit = XMLParser.get_unit(path_config_xml)
                            card = XMLParser.get_card_type(path_config_xml)
                            port_name = XMLParser.get_port_name(root_element)
                            freq = XMLParser.get_port_freq(root_element)
                            loc_color = (
                                location.replace(" ", "").replace("(", "_")
                            ).split(")")[0]
                            try:
                                color = self.colors[loc_color].value
                            except KeyError:
                                color = "black"
                            node = Node.Node(port_name, location, unit, freq, color)
                            self.diagram.add_node(node)

                            self.find_next_hop(root_element, location, node)

                            break

    def find_config_unit_name(self, location, unit):
        folders = self.get_folders(location)
        for folder in folders:
            path = os.path.join(self.root_folder, folder, "committed", unit)
            if not os.path.isdir(path):
                print(f"Folder ne postoji: {path}")
                break
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file == "common_config.xml":
                        return os.path.join(path, file)

    def find_next_hop(
        self, previous_port, config_dir, previous_node, connection=None, chan=None
    ):
        ports_data = []
        is_seli_port = XMLParser.is_seli_port(previous_port)
        if not is_seli_port:
            ports_data = XMLParser.get_seli_port(previous_port)
        elif chan is not None:
            path = os.path.join(self.root_folder, config_dir)
            config_xml_path = XMLParser.find_config_label(path, connection)
            for xml_path in config_xml_path:
                port = XMLParser.find_port_by_label(xml_path, connection)
                if chan is not None:
                    chan_name = XMLParser.get_chan(chan)
                    next_chan = XMLParser.get_chan_port(port, chan_name)
                    ports_data = XMLParser.get_seli_port(next_chan)
                unit = XMLParser.get_unit(xml_path)
                card = XMLParser.get_card_type(xml_path)
                port_name = XMLParser.get_port_name(port)
                chan = XMLParser.get_chan_port(port, chan_name)

                loc_color = (config_dir.replace(" ", "").replace("(", "_")).split(")")[
                    0
                ]
                try:
                    color = self.colors[loc_color].value
                except KeyError:
                    color = "black"
                node = Node.Node(port_name, config_dir, unit, chan_name, color)
                # self.diagram.add_node(node)
                # self.diagram.add_edge(previous_node, node, connection)
                # if self.diagram.add_node(node):
                #     self.diagram.add_edge(previous_node, node, connection)
                check, data = self.diagram.add_node(node)
                if check:
                    self.diagram.add_edge(previous_node, node, connection)
                else:
                    self.diagram.add_edge(previous_node, data, connection)
                previous_node = node
        for data in ports_data:
            port_element = data.split("/")
            next_config = self.find_config_unit_name(config_dir, port_element[1])
            port = XMLParser.get_port(next_config, port_element[2])
            unit = XMLParser.get_unit(next_config)
            card = XMLParser.get_card_type(next_config)
            port_name = XMLParser.get_port_name(port)
            if XMLParser.is_seli_port(port):
                chan = XMLParser.get_chan_port(port, port_element[3])
                chan_name = port_element[3]

                loc_color = (config_dir.replace(" ", "").replace("(", "_")).split(")")[
                    0
                ]
                try:
                    color = self.colors[loc_color].value
                except KeyError:
                    color = "black"
                node = Node.Node(port_name, config_dir, unit, chan_name, color)
                # self.diagram.add_node(node)
                # connection=XMLParser.get_port_label(port)
                # self.diagram.add_edge(previous_node, node, connection)
                # if self.diagram.add_node(node):
                #     connection=XMLParser.get_port_label(port)
                #     self.diagram.add_edge(previous_node, node, connection)
                check, data = self.diagram.add_node(node)
                connection = XMLParser.get_port_label(port)
                if check:
                    self.diagram.add_edge(previous_node, node, connection)
                else:
                    self.diagram.add_edge(previous_node, data, connection)

                next_hop_label = XMLParser.get_port_label(port)
                # connection = XMLParser.get_ll_rr(next_hop_label)
                # if connection is not None:
                #     locations = XMLParser.find_locations_label(
                #         self.root_folder, connection
                #     )
                #     locations = [loc for loc in locations if loc != config_dir]
                #     for loc in locations:
                #         self.find_next_hop(port, loc, node, connection, chan)
                # else:
                connection = self.conParser.find_connection(
                    f"{next_hop_label}/{config_dir}"
                )
                print(connection)
                next_mux_data = self.conParser.find_next_mux(
                    connection, f"{next_hop_label}/{config_dir}"
                )
                location_data = next_mux_data[0].split("/")
                folders = self.get_folders(location_data[1])
                for folder in folders:
                    self.find_next_hop(port, folder, node, location_data[0], chan)
            elif XMLParser.is_conf(port):
                loc_color = (config_dir.replace(" ", "").replace("(", "_")).split(")")[
                    0
                ]
                try:
                    color = self.colors[loc_color].value
                except KeyError:
                    color = "black"
                parts = XMLParser.get_parts_conf(port)
                for part in parts:
                    role = XMLParser.get_role(part)
                    part_name = XMLParser.get_part_name(part)
                    node = Node.Node(
                        port_element[2],
                        config_dir,
                        port_element[1],
                        part_name,
                        color,
                        role,
                    )
                    # self.diagram.add_node(node)
                    # self.diagram.add_edge(previous_node, node, connection)
                    check, data = self.diagram.add_node(node)
                    if check:
                        self.diagram.add_edge(previous_node, node, connection)
                    else:
                        self.diagram.add_edge(previous_node, data, connection)
                    self.find_next_hop(part, config_dir, node, connection)

            else:
                chan_name = ""
                loc_color = (config_dir.replace(" ", "").replace("(", "_")).split(")")[
                    0
                ]
                try:
                    color = self.colors[loc_color].value
                except KeyError:
                    color = "black"
                node = Node.Node(port_name, config_dir, unit, chan_name, color)
                # self.diagram.add_node(node)
                # self.diagram.add_edge(previous_node, node, connection)
                check, data = self.diagram.add_node(node)
                if check:
                    self.diagram.add_edge(previous_node, node, connection)
                else:
                    self.diagram.add_edge(previous_node, data, connection)
                return

    def find_next_location(self, label, previous_location):
        try:
            with open(self.connections_file, "r") as file:
                for line in file:
                    line = line.strip()  # uklanja \n i razmake
                    if line.startswith(label):
                        data = line.split("/")
                        return data[1] if data[1] != previous_location else data[2]
        except Exception as e:
            print(e)


if __name__ == "__main__":
    diag = Diagram_XML()

    root = tk.Tk()
    gui = GUI(root, diag)
    root.mainloop()
