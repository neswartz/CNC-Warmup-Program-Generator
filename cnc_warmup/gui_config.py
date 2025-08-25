import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass
from typing import Dict
from .config_loader import load_config, get_machines, get_defaults

"""Tkinter GUI to collect warmup configuration from the user."""


# Dataclass for the warmup config
@dataclass
class WarmupConfig:
    machine: str  # preset name selected (if any)
    controller: str
    program_name: str
    rpm_steps: int
    seconds_per_step: int
    x_travel: float
    y_travel: float
    z_travel: float
    start_rpm: float
    finish_rpm: float
    start_feed: float
    finish_feed: float
    coolant: bool

# GUI for the warmup config
class WarmupConfigGUI:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("CNC Warmup Program - Config")
        self.result: WarmupConfig | None = None
        self.root.geometry("420x360")
        self.root.resizable(False, False)

        # Load config
        cfg = load_config()
        machines = get_machines(cfg)
        defaults = get_defaults(cfg)

        # Main frame
        main = ttk.Frame(self.root, padding=20)
        main.grid(row=0, column=0, sticky="nsew")

        # Configure the root window
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Program settings
        ttk.Label(main, text="Program Name:").grid(row=0, column=0, sticky="w")
        self.program_name_var = tk.StringVar(value=str(defaults.get("program_name", "WARMUP")))
        ttk.Entry(main, textvariable=self.program_name_var).grid(row=0, column=1, sticky="ew")

        # Controller selection
        ttk.Label(main, text="Controller:").grid(row=1, column=0, sticky="w")
        controllers = ["Heidenhain TNC 640", "Fanuc 31i"]
        default_controller_key = str(defaults.get("controller", "tnc640"))
        default_controller_label = "Heidenhain TNC 640" if default_controller_key == "tnc640" else "Fanuc 31i"
        self.controller_var = tk.StringVar(value=default_controller_label)
        self.controller_combo = ttk.Combobox(main, textvariable=self.controller_var, values=controllers, state="readonly")
        self.controller_combo.grid(row=1, column=1, sticky="ew")

        # Start/Finish RPM
        ttk.Label(main, text="Start RPM:").grid(row=3, column=0, sticky="w")
        self.start_rpm_var = tk.StringVar(value=str(defaults.get("start_rpm", 500)))
        ttk.Entry(main, textvariable=self.start_rpm_var).grid(row=3, column=1, sticky="ew")

        ttk.Label(main, text="Finish RPM:").grid(row=4, column=0, sticky="w")
        self.finish_rpm_var = tk.StringVar(value=str(defaults.get("finish_rpm", 6000)))
        ttk.Entry(main, textvariable=self.finish_rpm_var).grid(row=4, column=1, sticky="ew")

        # Start/Finish Feed
        ttk.Label(main, text="Start Feed (mm/min):").grid(row=5, column=0, sticky="w")
        self.start_feed_var = tk.StringVar(value=str(defaults.get("start_feed", 1000)))    
        ttk.Entry(main, textvariable=self.start_feed_var).grid(row=5, column=1, sticky="ew")

        ttk.Label(main, text="Finish Feed (mm/min):").grid(row=6, column=0, sticky="w")
        self.finish_feed_var = tk.StringVar(value=str(defaults.get("finish_feed", 2000)))
        ttk.Entry(main, textvariable=self.finish_feed_var).grid(row=6, column=1, sticky="ew")

        # RPM Steps and Seconds per Step
        default_steps = int(defaults.get("rpm_steps", defaults.get("num_steps", 5)))
        ttk.Label(main, text="Steps (RPM):").grid(row=7, column=0, sticky="w")
        self.rpm_steps_var = tk.StringVar(value=str(default_steps))
        ttk.Entry(main, textvariable=self.rpm_steps_var).grid(row=7, column=1, sticky="ew")

        ttk.Label(main, text="Seconds per Step:").grid(row=8, column=0, sticky="w")
        self.seconds_per_step_var = tk.StringVar(value=str(int(defaults.get("seconds_per_step", 1))))
        ttk.Entry(main, textvariable=self.seconds_per_step_var).grid(row=8, column=1, sticky="ew")

        # Coolant
        self.coolant_var = tk.BooleanVar(value=bool(defaults.get("coolant", True)))
        ttk.Label(main, text="Flood Coolant (M8):").grid(row=9, column=0, sticky="w")
        ttk.Checkbutton(main, variable=self.coolant_var).grid(row=9, column=1, sticky="w")

        ttk.Separator(main, orient="horizontal").grid(row=10, column=0, columnspan=2, sticky="ew", pady=(10, 10))

        # Machine Travel Limit Preset selection
        ttk.Label(main, text="Travel Limit Preset:").grid(row=11, column=0, sticky="w")
        machine_names = (list(machines.keys()) + ["Custom"]) if machines else ["Custom"]
        self.machine_var = tk.StringVar(value=machine_names[0])
        self.machine_combo = ttk.Combobox(main, textvariable=self.machine_var, values=machine_names, state="readonly")
        self.machine_combo.grid(row=11, column=1, sticky="ew")

        # Machine Travel Limit (manual inputs)
        first_spec = machines.get(machine_names[0], {"x_travel": 300, "y_travel": 300, "z_travel": 300})
        ttk.Label(main, text="X Travel Limit (mm):").grid(row=12, column=0, sticky="w")
        self.x_travel_var = tk.StringVar(value=str(first_spec.get("x_travel", 300)))
        self.x_travel_entry = ttk.Entry(main, textvariable=self.x_travel_var)
        self.x_travel_entry.grid(row=12, column=1, sticky="ew")

        ttk.Label(main, text="Y Travel Limit (mm):").grid(row=13, column=0, sticky="w")
        self.y_travel_var = tk.StringVar(value=str(first_spec.get("y_travel", 300)))
        self.y_travel_entry = ttk.Entry(main, textvariable=self.y_travel_var)
        self.y_travel_entry.grid(row=13, column=1, sticky="ew")

        ttk.Label(main, text="Z Travel Limit (mm):").grid(row=14, column=0, sticky="w")
        self.z_travel_var = tk.StringVar(value=str(first_spec.get("z_travel", 300)))
        self.z_travel_entry = ttk.Entry(main, textvariable=self.z_travel_var)
        self.z_travel_entry.grid(row=14, column=1, sticky="ew")

        # OK/Cancel Buttons
        button_row = ttk.Frame(main)
        button_row.grid(row=15, column=0, columnspan=2, sticky="e", pady=(8, 0))

        ttk.Button(button_row, text="Cancel", command=self.root.destroy).grid(row=0, column=0, padx=(0, 6))
        ttk.Button(button_row, text="OK", command=self._on_ok).grid(row=0, column=1)

        # Configure the main frame
        for i in range(2):
            main.columnconfigure(i, weight=1)

        # Bind preset selection to populate travel fields
        self.machine_combo.bind("<<ComboboxSelected>>", self._on_preset_change)
        self._machines = machines

        # Initialize travel field enabled state based on selection (disable if not Custom)
        self._set_travel_entries_state(self.machine_var.get() == "Custom")

    # On OK button click
    def _on_ok(self) -> None:
        try:
            program_name = str(self.program_name_var.get()).strip() or "WARMUP"
            rpm_steps = int(self.rpm_steps_var.get())
            seconds_per_step = int(self.seconds_per_step_var.get())
            start_rpm = float(self.start_rpm_var.get())
            finish_rpm = float(self.finish_rpm_var.get())
            start_feed = float(self.start_feed_var.get())
            finish_feed = float(self.finish_feed_var.get())
            x_travel = float(self.x_travel_var.get())
            y_travel = float(self.y_travel_var.get())
            z_travel = float(self.z_travel_var.get())
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter numeric values (e.g., 123 or 123.4) for RPM, feed rates, and travels.")
            return

        self.result = WarmupConfig(
            machine=self.machine_var.get(),
            controller=self.controller_var.get(),
            program_name=program_name,
            rpm_steps=max(1, rpm_steps),
            seconds_per_step=max(0, seconds_per_step),
            x_travel=x_travel,
            y_travel=y_travel,
            z_travel=z_travel,
            start_rpm=start_rpm,
            finish_rpm=finish_rpm,
            start_feed=start_feed,
            finish_feed=finish_feed,
            coolant=self.coolant_var.get(),
        )
        self.root.destroy()

    def _on_preset_change(self, event: object) -> None:
        name = self.machine_var.get()
        if name == "Custom":
            self._set_travel_entries_state(True)
            return
        spec = self._machines.get(name)
        if not spec:
            return
        # Populate travel fields from preset and disable editing
        self.x_travel_var.set(str(spec.get("x_travel", 300)))
        self.y_travel_var.set(str(spec.get("y_travel", 300)))
        self.z_travel_var.set(str(spec.get("z_travel", 300)))
        self._set_travel_entries_state(False)

    def _set_travel_entries_state(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        self.x_travel_entry.configure(state=state)
        self.y_travel_entry.configure(state=state)
        self.z_travel_entry.configure(state=state)


# Launch the GUI and get the config
def launch_gui_and_get_config() -> WarmupConfig | None:
    gui = WarmupConfigGUI()
    gui.root.mainloop()
    return gui.result


