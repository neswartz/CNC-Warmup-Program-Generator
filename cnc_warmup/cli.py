import argparse
import sys
from tkinter import filedialog, messagebox

from .generators import generate_tnc_program, generate_fanuc_program
from .gui_config import launch_gui_and_get_config
from .config_loader import load_config, get_defaults


def main() -> None:
    # Load defaults for both GUI and CLI
    config = load_config()
    defaults = get_defaults(config)

    # If any CLI args are provided (beyond the script name), use CLI mode
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description="Generate CNC warmup program")
        parser.add_argument("--program-name", default=str(defaults.get("program_name", "WARMUP")))
        parser.add_argument(
            "--controller",
            choices=["tnc640", "fanuc31i"],
            default=str(defaults.get("controller", "tnc640")),
        )
        parser.add_argument("--x-travel", type=float, required=True)
        parser.add_argument("--y-travel", type=float, required=True)
        parser.add_argument("--z-travel", type=float, required=True)
        parser.add_argument("--start-rpm", type=float, default=float(defaults.get("start_rpm", 500)))
        parser.add_argument("--finish-rpm", type=float, default=float(defaults.get("finish_rpm", 6000)))
        parser.add_argument("--start-feed", type=float, default=float(defaults.get("start_feed", 1000)))
        parser.add_argument("--finish-feed", type=float, default=float(defaults.get("finish_feed", 2000)))
        parser.add_argument("--rpm-steps", type=int, default=int(defaults.get("rpm_steps", defaults.get("num_steps", 5))))
        parser.add_argument("--seconds-per-step", type=int, default=int(defaults.get("seconds_per_step", 1)))
        parser.add_argument("--coolant", dest="coolant", action="store_true", default=bool(defaults.get("coolant", False)))
        parser.add_argument("--output", default="", help="Output file path (defaults to stdout)")

        args = parser.parse_args()
        gen_func = generate_tnc_program if args.controller == "tnc640" else generate_fanuc_program
        # Determine machine label from CLI (no presets here; allow explicit label)
        machine_label = None
        program_text = gen_func(
            program_name=args.program_name,
            x_travel=args.x_travel,
            y_travel=args.y_travel,
            z_travel=args.z_travel,
            start_feed_mm_min=args.start_feed,
            finish_feed_mm_min=args.finish_feed,
            steps=int(args.rpm_steps),
            start_rpm=args.start_rpm,
            finish_rpm=args.finish_rpm,
            seconds_per_step=max(0, int(args.seconds_per_step)),
            include_coolant=bool(args.coolant),
            machine_label=machine_label,
        )

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(program_text)
        else:
            print(program_text, end="")
        return

    # Otherwise, run the GUI flow
    cfg = launch_gui_and_get_config()
    if cfg is None:
        return

    program_name = str(getattr(cfg, "program_name", defaults.get("program_name", "WARMUP")))
    rpm_steps = int(getattr(cfg, "rpm_steps", int(defaults.get("rpm_steps", defaults.get("num_steps", 5)))))
    seconds_per_step = int(getattr(cfg, "seconds_per_step", int(defaults.get("seconds_per_step", 1))))

    controller_label = str(getattr(cfg, "controller", "Heidenhain TNC 640"))
    gen_func = generate_tnc_program if controller_label.startswith("Heidenhain") else generate_fanuc_program

    # Machine label for header
    selected_machine = str(getattr(cfg, "machine", ""))
    machine_label = selected_machine if selected_machine and selected_machine != "Custom" else "Custom"

    program_text = gen_func(
        program_name=program_name,
        x_travel=cfg.x_travel,
        y_travel=cfg.y_travel,
        z_travel=cfg.z_travel,
        start_feed_mm_min=cfg.start_feed,
        finish_feed_mm_min=cfg.finish_feed,
        steps=rpm_steps,
        start_rpm=cfg.start_rpm,
        finish_rpm=cfg.finish_rpm,
        seconds_per_step=max(0, seconds_per_step),
        include_coolant=cfg.coolant,
        machine_label=machine_label,
    )

    if gen_func is generate_tnc_program:
        defext = ".h"
        ftypes = [("Heidenhain Program", ".h"), ("Text", ".txt"), ("All Files", "*.*")]
    else:
        defext = ".nc"
        ftypes = [("Fanuc Program", ".nc"), ("Text", ".txt"), ("All Files", "*.*")]

    path = filedialog.asksaveasfilename(
        title="Save Warmup Program",
        defaultextension=defext,
        filetypes=ftypes,
        initialfile=f"{program_name}{defext}",
    )
    if path:
        with open(path, "w", encoding="utf-8") as f:
            f.write(program_text)
        messagebox.showinfo("Saved", f"Program saved to: {path}")
    else:
        try:
            from tkinter import Tk
            root = Tk()
            root.withdraw()
            messagebox.showinfo("Program", program_text[:1000] + ("..." if len(program_text) > 1000 else ""))
            root.destroy()
        except Exception:
            print(program_text)



