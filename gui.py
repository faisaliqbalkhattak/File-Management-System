# gui.py
# This file implements the GUI (Graphical User Interface) for the Virtual File System using tkinter.
# It allows users to perform file system operations through buttons, menus, and a command-line entry box.

import tkinter as tk
from tkinter import messagebox, simpledialog
from fs import VirtualFileSystem   # Importing the backend logic
import os

class VFSApp:
    def __init__(self, master):
        # Initialize main window properties
        self.master = master
        master.title("Virtual File System GUI")
        master.configure(bg="#f0f0f0")    # Light background color
        master.geometry("900x600")        # Set window size
        master.grid_rowconfigure(2, weight=1)  # Allow text area to expand
        master.grid_rowconfigure(5, weight=1)  # Allow file list area to expand

        self.vfs = VirtualFileSystem()    # Create an instance of the virtual file system
        self.history = []                 # Stores command history
        self.history_index = -1           

        # Configure main window grid (layout)
        for i in range(3):
            master.grid_columnconfigure(i, weight=1)
        master.grid_rowconfigure(3, weight=1)

        # Add main title label
        self.label = tk.Label(master, text="Virtual File System", font=("Helvetica", 18, "bold"),
                              bg="#3e3e3e", fg="white", pady=10)
        self.label.grid(row=0, column=0, columnspan=3, sticky="ew")

        # Label to show current path
        self.path_label = tk.Label(master, text="Current Path: /", font=("Helvetica", 10),
                                   bg="#dfe6e9", anchor="w")
        self.path_label.grid(row=1, column=0, columnspan=3, sticky="ew")

        # Text area for output messages
        self.output = tk.Text(master, height=10, wrap="word", bg="#fdfdfd", fg="#2d3436", state=tk.DISABLED, bd=1, relief="solid")
        self.output.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=10, pady=5)

        # Entry box for entering commands
        self.command_entry = tk.Entry(master, width=70, bg="#ffffff", bd=1, relief="solid")
        self.command_entry.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        self.command_entry.bind("<Return>", lambda e: self.run_command())  # Enter key runs command
        self.command_entry.bind("<Up>", self.navigate_history_up)          # Up key for history
        self.command_entry.bind("<Down>", self.navigate_history_down)      # Down key for history

        # Run button to execute the command
        self.run_button = tk.Button(master, text="Run", command=self.run_command,
                            bg="#74b9ff", fg="white", 
                            highlightbackground="blue", highlightthickness=2, 
                            padx=10, pady=1)  
        self.run_button.grid(row=3, column=1, sticky="ew", padx=5)

        # Frame for bottom buttons (Clear, Browse, Create, Help, Exit)
        button_frame = tk.Frame(master, bg="#f0f0f0")
        button_frame.grid(row=4, column=0, columnspan=3, pady=5, sticky="ew")

        btn_config = {"bg": "#74b9ff", "fg": "white", "padx": 5, "pady": 2,
                      "highlightbackground": "#FF7518", "highlightthickness": 2}
        tk.Button(button_frame, text="Clear", command=self.clear_output, **btn_config).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Browse Dir", command=self.browse_dir, **btn_config).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Create File", command=self.create_file, **btn_config).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Help", command=self.show_help, **btn_config).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Exit", command=master.quit, **btn_config).pack(side=tk.LEFT, padx=5)

        # Context menu when right-clicking on files
        self.file_menu = tk.Menu(master, tearoff=0)
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Delete", command=self.delete_file)

        # Context menu when right-clicking on empty space
        self.blank_menu = tk.Menu(master, tearoff=0)
        self.blank_menu.add_command(label="Create Folder", command=self.create_folder)
        self.blank_menu.add_command(label="Create File", command=self.create_file)
        self.blank_menu.add_command(label="Help", command=self.show_help)

        # List box to display files and folders
        self.file_listbox = tk.Listbox(master, height=10, bg="#ecf0f1", fg="#2d3436", bd=1, relief="solid")
        self.file_listbox.grid(row=5, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)
        self.file_listbox.bind("<Button-3>", self.on_listbox_right_click)  # Right click
        self.file_listbox.bind("<Double-Button-1>", self.on_double_click)  # Double click

        self.selected_file_name = None  # Keeps track of selected file/folder

    # ----------------------- COMMANDS HANDLER ---------------------------

    # Runs the command entered in the entry box
    def run_command(self):
        cmd_line = self.command_entry.get().strip()
        cmd = cmd_line.split()
        if not cmd:
            return

        self.history.append(cmd_line)
        self.history_index = len(self.history)

        out = ""  # Output string

        # Process different commands
        if cmd[0] == "create" and len(cmd) == 2:
            out = self.vfs.create(cmd[1])
        elif cmd[0] == "del" and len(cmd) == 2:
            out = self.vfs.delete(cmd[1])
        elif cmd[0] == "mkdir" and len(cmd) == 2:
            out = self.vfs.mkdir(cmd[1])
        elif cmd[0] == "chdir" and len(cmd) == 2:
            out = self.vfs.chdir(cmd[1])
        elif cmd[0] == "move" and len(cmd) == 3:
            out = self.vfs.move(cmd[1], cmd[2])
        elif cmd[0] == "open" and len(cmd) == 2:
            out = str(self.vfs.open(cmd[1]))
        elif cmd[0] == "ls":
            out = "\n".join(self.vfs.ls())
        elif cmd[0] == "memmap":
            out = self.vfs.show_memory_map()
        elif cmd[0] == "read_start_len" and len(cmd) == 4:
            start = int(cmd[2])
            size = int(cmd[3])
            out = self.vfs.read_from(cmd[1], start, size)
        elif cmd[0] == "move_within" and len(cmd) == 5:
            start = int(cmd[2])
            size = int(cmd[3])
            target = int(cmd[4])
            out = self.vfs.move_within_file(cmd[1], start, size, target)
        elif cmd[0] == "truncate" and len(cmd) == 3:
            size = int(cmd[2])
            out = self.vfs.truncate(cmd[1], size)
        elif cmd[0] == "write" and len(cmd) >= 3:
            file = self.vfs.open(cmd[1])
            if file:
                file.write(" ".join(cmd[2:]))
                self.vfs.save_fs()
                out = "Text written."
            else:
                out = "File not found."
        elif cmd[0] == "write_at" and len(cmd) >= 4:
            index = int(cmd[2])
            out = self.vfs.write_at(cmd[1], index, " ".join(cmd[3:]))
        elif cmd[0] == "read" and len(cmd) == 2:
            file = self.vfs.open(cmd[1])
            if file:
                out = file.read()
            else:
                out = "File not found."
        else:
            out = "Invalid or unsupported command. Click Help for usage."

        self.append_output(f"> {cmd_line}\n{out}\n")
        self.command_entry.delete(0, tk.END)
        self.path_label.config(text=f"Current Path: {'/'.join(self.vfs.cwd)}")

    # Append text to the output display
    def append_output(self, text):
        self.output.config(state=tk.NORMAL)
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)
        self.output.config(state=tk.DISABLED)

    # Clears the output area
    def clear_output(self):
        self.output.config(state=tk.NORMAL)
        self.output.delete("1.0", tk.END)
        self.output.config(state=tk.DISABLED)

    # Refresh the file/folder list
    def browse_dir(self):
        self.file_listbox.delete(0, tk.END)
        for file in self.vfs.ls():
            self.file_listbox.insert(tk.END, file)

    # Show help information
    def show_help(self):
        help_text = (
          "Commands:\n"
          "open <file>      - Open file\n"
          "read <file>      - Read file\n"
          "close <file>     - Close file\n"
          "create <file>    - Create file\n"
          "ls               - List contents\n"  
          "memmap           - Show memory map\n"        
          "mkdir <dir>      - Create directory\n"    
          "chdir <dir>      - Change directory\n"
          "write <file><text> - Write text to file\n"
          "del <file|dir>    - Delete file or directory\n"
          "truncate <file> <size> - Truncate file to size\n"
          "write_at <file> <index> <text> - Write at position\n"
          "read_start_len <file> <start> <len> - Read partial content\n"
          "move_within <file> <start> <len> <target> - Move content inside file\n"
          "Right-click to access menu options."
        )
        messagebox.showinfo("Help", help_text)

    # Prompt user to create a new file
    def create_file(self):
        filename = simpledialog.askstring("Create File", "Enter the filename:")
        if filename:
            out = self.vfs.create(filename)
            self.append_output(f"{out}")
            self.vfs.save_fs()

    # Prompt user to create a new folder
    def create_folder(self):
        dirname = simpledialog.askstring("Create Folder", "Enter the folder name:")
        if dirname:
            out = self.vfs.mkdir(dirname)
            self.append_output(f"{out}")
            self.vfs.save_fs()
            self.browse_dir()

    # Open a selected file
    def open_file(self):
        if self.selected_file_name:
            selected_file = self.vfs.open(self.selected_file_name)
            if selected_file:
                content = selected_file.read()
                self.append_output(f"Content of {self.selected_file_name}:\n{content}")
            else:
                self.append_output(f"File '{self.selected_file_name}' not found.\n")
        else:
            self.append_output("No file selected to open.\n")

    # Delete a selected file or folder
    def delete_file(self):
        if self.selected_file_name:
            items = self.vfs.ls()
            is_dir = self.selected_file_name not in [f for f in items if '.' in f]
            self.vfs.delete(self.selected_file_name)
            self.append_output(
                f"{'Directory' if is_dir else 'File'} '{self.selected_file_name}' deleted.\n"
            )
            self.vfs.save_fs()
            self.browse_dir()
        else:
            self.append_output("No file selected to delete.\n")

    # Handle right-click events
    def on_listbox_right_click(self, event):
        index = self.file_listbox.nearest(event.y)
        bbox = self.file_listbox.bbox(index)
        if not bbox or not (bbox[1] <= event.y <= bbox[1] + bbox[3]):
            self.selected_file_name = None
            self.blank_menu.tk_popup(event.x_root, event.y_root)
        else:
            self.selected_file_name = self.file_listbox.get(index)
            self.file_menu.tk_popup(event.x_root, event.y_root)

    # Handle double-click events
    def on_double_click(self, event):
        selection = self.file_listbox.curselection()
        if selection:
            name = self.file_listbox.get(selection[0])
            if '.' in name:
                self.selected_file_name = name
                self.open_file()
            else:
                self.vfs.chdir(name)
                self.path_label.config(text=f"Current Path: {'/'.join(self.vfs.cwd)}")
                self.browse_dir()

    # Navigate through command history (up arrow key)
    def navigate_history_up(self, event):
        if self.history and self.history_index > 0:
            self.history_index -= 1
            self.command_entry.delete(0, tk.END)
            self.command_entry.insert(0, self.history[self.history_index])

    # Navigate through command history (down arrow key)
    def navigate_history_down(self, event):
        if self.history and self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.command_entry.delete(0, tk.END)
            self.command_entry.insert(0, self.history[self.history_index])
        else:
            self.command_entry.delete(0, tk.END)
            self.history_index = len(self.history)

# If this file is run directly, start the app
if __name__ == "__main__":
    root = tk.Tk()
    app = VFSApp(root)
    root.mainloop()
