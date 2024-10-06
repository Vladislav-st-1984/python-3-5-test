import os
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import ttk
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class DeviceTreeApp(tk.Tk):
    def __init__(self, xml_path, folder_to_monitor):
        super().__init__()
        self.title("Device Monitoring")
        self.geometry("600x400")

        # Treeview widget with columns
        self.tree = ttk.Treeview(self, columns=("name"), show="tree headings")
        self.tree.heading("#0", text="Device Type")
        self.tree.heading("name", text="Device Name")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Store the paths
        self.xml_path = xml_path
        self.folder_to_monitor = folder_to_monitor

        # Initial load of the XML data
        self.load_xml_data()

        # Setup folder monitoring
        self.setup_folder_monitoring()

    def load_xml_data(self):
        """Load and parse the XML file, then populate the tree"""
        # Clear any existing items in the tree
        for i in self.tree.get_children():
            self.tree.delete(i)

        try:
            # Parse the XML file
            tree = ET.parse(self.xml_path)
            root = tree.getroot()

            # Recursively add the XML elements to the tree
            self.populate_tree("", root)
        except ET.ParseError as e:
            print("Error parsing XML file:", e)
        except FileNotFoundError:
            print("XML file not found")

    def populate_tree(self, parent, element):
        """Recursively add XML elements to the tree with device names"""
        # Get the device name from the 'name' attribute if it exists
        device_name = element.attrib.get("name", element.tag)  # Default to the tag if no name is found

        # Insert the item in the tree, adding the device name
        if parent == "":
            node = self.tree.insert("", "end", text=element.tag, values=(device_name,))  # Root node
        else:
            node = self.tree.insert(parent, "end", text=element.tag, values=(device_name,))  # Child nodes

        # Recursively add children
        for child in element:
            self.populate_tree(node, child)

    def setup_folder_monitoring(self):
        """Setup monitoring for changes in the folder"""
        event_handler = FolderChangeHandler(self.xml_path, self.load_xml_data)
        observer = Observer()
        observer.schedule(event_handler, self.folder_to_monitor, recursive=False)
        observer.start()


class FolderChangeHandler(FileSystemEventHandler):
    def __init__(self, xml_path, callback):
        super().__init__()
        self.xml_path = xml_path
        self.callback = callback

    def on_modified(self, event):
        """Handle file modification events"""
        if event.src_path == self.xml_path:
            print(f"Detected change in {self.xml_path}, reloading XML data.")
            self.callback()


if __name__ == "__main__":
    xml_path = "data.xml"  # Path to the XML file
    folder_to_monitor = "."  # Folder to monitor for changes

    app = DeviceTreeApp(xml_path, folder_to_monitor)
    app.mainloop()