# CNC Warmup Program Generator

Generate safe, parameterized warmup programs for CNC machines.

Supports:

- Heidenhain TNC 640 (Klartext)
- Fanuc 31i (G-code)

Use it two ways:

- GUI: interactive form
- CLI: scriptable with flags

## Requirements

- Python 3.10 or newer

## Quick Start (GUI)

### Windows shortcut

- Double-click `run_gui.bat` to open the GUI.

### Terminal command

1. Open a terminal in the project folder.
2. Run the app with no arguments to launch the GUI:

```bash
python -m cnc_warmup
```

1. In the GUI:
   - Set Program Name, Controller, optional Machine preset or "Custom" travels
   - Start/Finish RPM and Feed, RPM Steps, Seconds per Step, Coolant
2. Click OK and choose where to save.

## Command-Line Usage (CLI)

- Show help:

```bash
python -m cnc_warmup --help
```

- Required flags: `--x-travel`, `--y-travel`, `--z-travel`
- Optional flags: `--program-name`, `--controller {tnc640|fanuc31i}`, `--start-rpm`, `--finish-rpm`, `--start-feed`, `--finish-feed`, `--rpm-steps`, `--seconds-per-step`, `--coolant`, `--output`

Examples:

```bash
# Heidenhain TNC 640, write to file
python -m cnc_warmup --controller tnc640 --program-name WARMUP --x-travel 762 --y-travel 508 --z-travel 500 --start-rpm 500 --finish-rpm 6000 --start-feed 1000 --finish-feed 2000 --rpm-steps 5 --seconds-per-step 60 --coolant --output warmup.h

# Fanuc 31i, print to stdout
python -m cnc_warmup --controller fanuc31i --x-travel 1016 --y-travel 660 --z-travel 500 --start-rpm 500 --finish-rpm 6000 --start-feed 1000 --finish-feed 2000 --rpm-steps 5 --seconds-per-step 60
```

Notes:

- Any CLI argument triggers CLI mode; otherwise, the GUI opens.
- Without `--output`, the program is printed to stdout.

## Configuration

Defaults and machine presets live in `config/warmup_config.json`:

```json
{
  "machines": {
    "Machine 1": { "x_travel": 762,  "y_travel": 508,  "z_travel": 500 },
    "Machine 2": { "x_travel": 1016, "y_travel": 660,  "z_travel": 500 },
    "Machine 3": { "x_travel": 1270, "y_travel": 508,  "z_travel": 500 }
  },
  "defaults": {
    "program_name": "WARMUP",
    "controller": "tnc640",
    "start_rpm": 500,
    "finish_rpm": 6000,
    "start_feed": 1000,
    "finish_feed": 2000,
    "coolant": false,
    "rpm_steps": 5,
    "seconds_per_step": 60
  }
}
```

- `defaults` seed both GUI fields and CLI defaults (unless overridden by flags).

## Docs

Reference manuals are included under `docs/` for convenience:

- Heidenhain TNC 640 Klartext Programming User's Manual
- Fanuc 30i Series Programming Manual

Also usedthe following websites as a reference:
- [https://www.helmancnc.com/](https://www.helmancnc.com/)
- [HIT – HEIDENHAIN Interactive Training](https://www.heidenhain.us/addl-materials/HIT_3-Axis-Programming_DEMO/index/hitheidenhai.html)
