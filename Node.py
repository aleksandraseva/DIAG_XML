class Node:
    def __init__(self, port, location, unit, ts, color,role=""):
        self.port = port
        self.location = location
        self.unit = unit
        self.ts = ts.replace("chan", "TS")
        self.role=role

        self.color = color

    def get_label(self):
        return f"{self.location}\n {self.port} {self.unit} \n{self.ts}\n{self.role}"
