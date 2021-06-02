import sublime
import os
import sublime_plugin
import json
import time


DEFAULT_STORAGE = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "timManagerStorage.json"


def set_default_storage():
    print("generate default storage")
    with open(DEFAULT_STORAGE, "w") as f:
        json.dump({}, f)


def plugin_loaded():
    if not os.path.exists(DEFAULT_STORAGE):
        set_default_storage()


def dump_time(extension, working_time):
    with open(DEFAULT_STORAGE) as f:
        data = json.load(f)
    if extension not in data:
        data[extension] = 0
    data[extension] += working_time
    with open(DEFAULT_STORAGE, "w") as f:
        json.dump(data, f)


def format_time(t):
    h = t // 60 // 60
    t -= h * 60 * 60
    m = t // 60
    s = t - (m * 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


class SetTimeManagerToDefaultCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        set_default_storage()


class TimeManagerReportCommand(sublime_plugin.TextCommand):
    def prepare_text(self):
        with open(DEFAULT_STORAGE) as f:
            data = json.load(f)
        
        text = "Time manager report:\n"
        for (ext, t) in data.items():
            text += f"{ext}: {format_time(t)}\n"
        return text
    
    def show_report(self, edit):
        text = self.prepare_text()
        w = sublime.active_window()
        v = w.new_file()
        v.insert(edit, 0, text)
        v.set_read_only(True)

    def run(self, edit):
        self.show_report(edit)


class TimeListener(sublime_plugin.ViewEventListener):
    def __init__(self, *args, **kwargs):
        self.extension = ""
        self.start_time = int(time.time())
        super().__init__(*args, **kwargs)

    def on_activated(self):
        if(self.view.file_name() is None):
            return
        self.extension = self.view.file_name().split(".")[-1] 
        self.start_time = int(time.time())
        print(f"Activated: {self.view.file_name()}")

    def on_deactivated(self):
        if(self.view.file_name() is None):
            return
        end_time = int(time.time())
        dump_time(str(self.extension), end_time - self.start_time)
        print(f"Deactivated: {self.view.file_name()}")