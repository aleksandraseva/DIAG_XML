import tkinter as tk
from tkinter import Canvas, Scrollbar
import networkx as nx
import math


class Diagram:
    def __init__(self):
        self.G = nx.DiGraph()

    def add_node(self, node):
        key = (
        node.port,
        node.location,
        node.unit,
        node.ts,
        node.color,
        node.role,
        )   
        for data in self.G.nodes:
            existing_key = (
            data.port,
            data.location,
            data.unit,
            data.ts,
            data.color,
            data.role,
            )

            if key == existing_key:
                return False,data

        self.G.add_node(node, label=node.get_label(), color=node.color)
        # self.G.add_node(node,port=node.port,location=node.location,unit=node.unit,ts=node.ts,color=node.color,role=node.role, label=node.get_label())
        return True,None

    def add_edge(self, nodeX, nodeY, connection):
        self.G.add_edge(nodeX, nodeY, connection=connection)

    def hierarchy_pos(self, root=None, vert_gap=150):
        pos = {}
        sizes = {}

        def _get_size(node):
            label = self.G.nodes[node]['label']
            lines = label.split("\n")
            max_len = max(len(line) for line in lines)
            w = max(80, 10 * max_len)
            h = max(40, 20 * len(lines))
            sizes[node] = (w, h)
            return w

        def _recurse(node, x_start, y_level):
            children = list(self.G.successors(node))
            if not children:
                w, h = sizes[node]
                pos[node] = (x_start + w // 2 - 10, y_level)
                return w
            total_width = 0
            for c in children:
                w_c = _recurse(c, x_start + total_width, y_level + vert_gap)
                total_width += w_c + 20
            w, h = sizes[node]
            pos[node] = (x_start + total_width // 2 - 10, y_level)
            return total_width

        if root is None:
            roots = [n for n in self.G.nodes if self.G.in_degree(n) == 0]
            if not roots:
                raise ValueError("Na lokaciji nema data frekvencija")
            root = roots[0]

        for node in self.G.nodes:
            _get_size(node)

        _recurse(root, 50, 100)
        return pos, sizes

    def _get_edge_points_diagonal(self, x0, y0, w0, h0, x1, y1, w1, h1):
        dx = x1 - x0
        dy = y1 - y0
        if dx == 0 and dy == 0:
            return x0, y0, x1, y1

        if dx == 0:
            scale0 = h0 / 2 / abs(dy)
            scale1 = h1 / 2 / abs(dy)
        elif dy == 0:
            scale0 = w0 / 2 / abs(dx)
            scale1 = w1 / 2 / abs(dx)
        else:
            scale0 = min(w0/2/abs(dx), h0/2/abs(dy))
            scale1 = min(w1/2/abs(dx), h1/2/abs(dy))

        start_x = x0 + dx * scale0
        start_y = y0 + dy * scale0
        end_x = x1 - dx * scale1
        end_y = y1 - dy * scale1

        return start_x, start_y, end_x, end_y

    def diagram_draw(self,main_root=None):
        margin_x = 100
        margin_y = 300
        pos, sizes = self.hierarchy_pos()

        all_x = [x for x, y in pos.values()]
        all_y = [y for x, y in pos.values()]
        width = max(all_x) + 200 + margin_x
        height = max(all_y) + 200 + margin_y

        root = tk.Toplevel()
        root.title("Mux")

        def on_close():
            root.destroy()
            if main_root is not None:
                main_root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_close)

        hbar = Scrollbar(root, orient=tk.HORIZONTAL)
        hbar.pack(side=tk.BOTTOM, fill=tk.X)
        vbar = Scrollbar(root, orient=tk.VERTICAL)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas = Canvas(root, width=800, height=600,
                        scrollregion=(0, 0, width, height),
                        xscrollcommand=hbar.set, yscrollcommand=vbar.set, bg="white")
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        hbar.config(command=canvas.xview)
        vbar.config(command=canvas.yview)


        for src, dst in self.G.edges:
            x0, y0 = pos[src]
            x1, y1 = pos[dst]
            w0, h0 = sizes[src]
            w1, h1 = sizes[dst]

            start_x, start_y, end_x, end_y = self._get_edge_points_diagonal(
                x0, y0, w0, h0, x1, y1, w1, h1)
            canvas.create_line(start_x, start_y, end_x, end_y,
                               arrow=tk.LAST, width=2, fill="black")

            mid_x = (start_x + end_x) / 2
            mid_y = (start_y + end_y) / 2


            offset = 45 
            text_x = mid_x + offset
            text_y = mid_y

            canvas.create_text(text_x, text_y, text=self.G.edges[src, dst].get('connection', ''),
                               font=("Arial", 10, "italic"), fill="darkred")


        for node in self.G.nodes:
            x, y = pos[node]
            w, h = sizes[node]
            color = self.G.nodes[node].get('color', 'lightblue')
            canvas.create_rectangle(x - w//2, y - h//2, x + w//2, y + h//2,
                                    fill=color, outline="black", width=2)
            canvas.create_text(x, y, text=self.G.nodes[node]['label'],
                               font=("Arial", 12, "bold"), justify="center", fill="white")

        root.mainloop()
