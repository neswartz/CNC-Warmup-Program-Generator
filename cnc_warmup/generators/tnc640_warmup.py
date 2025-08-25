from typing import List

"""

Heidenhain TNC 640 warmup program generator.

This module produces a Q-variable driven warmup program that exercises Z and XY
axes and performs a spindle warmup with incremental steps and dwell times.

Notes:
Warmup is done from the machine datum point, which is assumed to be in the corner of the machine.

"""

# Convert float to string
def _format_number(value: float) -> str:
    if float(value).is_integer():
        return str(int(value))
    s = f"{value:.6f}".rstrip("0").rstrip(".")
    return s if s else "0"

# Generate the warmup program text.
def generate_program(
    program_name: str,
    x_travel: float,
    y_travel: float,
    z_travel: float,
    start_feed_mm_min: float,
    finish_feed_mm_min: float,
    steps: int,
    start_rpm: float,
    finish_rpm: float,
    seconds_per_step: int,
    include_coolant: bool = True,
    machine_label: str | None = None,
) -> str:

    # Format a single Q-variable definition line with an inline comment.
    def q_line(q: int, value: float, comment: str) -> str:
        val = _format_number(value)
        return f"Q{q} = {val:>6}    ; {comment}"

    clamped_steps = max(1, int(steps))
    clamped_dwell = max(0, int(seconds_per_step))

    lines: List[str] = []
    lines.append(f"BEGIN PGM {program_name} MM")
    if machine_label:
        lines.append(f"; MACHINE: {machine_label}")

    # Config
    lines.append("; ===== Config =====")
    lines.append(q_line(1, 0, "X_MIN_SAFE (mm)"))
    lines.append(q_line(2, x_travel, "X_MAX_SAFE"))
    lines.append(q_line(3, 0, "Y_MIN_SAFE"))
    lines.append(q_line(4, y_travel, "Y_MAX_SAFE"))
    lines.append(q_line(5, 0, "Z_TOP_SAFE"))
    lines.append(q_line(6, -z_travel, "Z_BOTTOM_SAFE"))
    lines.append("")
    lines.append(q_line(10, start_feed_mm_min, "FEED_START (mm/min)"))
    lines.append(q_line(11, finish_feed_mm_min, "FEED_FIN"))   
    lines.append("")
    lines.append(q_line(20, start_rpm, "RPM_START"))
    lines.append(q_line(21, finish_rpm, "RPM_FIN"))
    lines.append(q_line(22, clamped_steps, "RPM_STEPS"))
    lines.append(q_line(23, clamped_dwell, "DWELL PER STEP (s)"))
    lines.append("")

    # Safe start
    lines.append("; ===== Safe start =====")
    lines.append("M5 M9")
    lines.append("PLANE RESET")
    lines.append("TRANS DATUM RESET")
    lines.append("FUNCTION RESET TCPM")
    lines.append("TOOL CALL 0 Z")
    if include_coolant:
        lines.append("M8")

    # Compute the feed and RPM increments
    lines.append("Q80 = +Q11 - Q10        ; FEED_RANGE")
    lines.append("Q81 = Q80/3             ; FEED_INC")
    lines.append("Q83 = (Q21 - Q20)/Q22   ; RPM_INC")
    lines.append("")

    # Move to safe Z
    lines.append("L  Z+Q5 FMAX M91  ; to safe Z")

    # Z axis test: Z top -> Z bottom -> Z top with feeds from start -> finish
    lines.append("; ===== Z axis test: top -> bottom -> top with increasing feed from start to finish =====")
    lines.append("Q100 = Q10")
    lines.append("L  Z+Q6 FQ100 M91        ; to Z bottom at start feed")
    lines.append("Q100 = Q10 + Q81")
    lines.append("L  Z+Q5 FQ100 M91        ; back to Z top at start+1/3 range")
    lines.append("Q100 = Q10 + Q81*2")
    lines.append("L  Z+Q6 FQ100 M91        ; to Z bottom at start+2/3 range")
    lines.append("Q100 = Q11")
    lines.append("L  Z+Q5 FQ100 M91        ; back to Z top at finish feed")
    lines.append("")

    # XY axis test: min -> max -> min with feeds from start -> finish
    lines.append("; ===== XY axis test: min -> max -> min with increasing feed from start to finish =====")
    lines.append("L  Z+Q5 FMAX M91         ; ensure safe Z for XY motion")
    lines.append("L  X+Q1  Y+Q3 FQ10 M91   ; go to min corner (0,0) with start feed")
    lines.append("Q100 = Q10")
    lines.append("L  X+Q2  Y+Q4 FQ100 M91  ; to max corner at start feed")
    lines.append("Q100 = Q10 + Q81")
    lines.append("L  X+Q1  Y+Q3 FQ100 M91  ; back to min corner at start+1/3 range")
    lines.append("Q100 = Q10 + Q81*2")
    lines.append("L  X+Q2  Y+Q4 FQ100 M91  ; to max corner at start+2/3 range")
    lines.append("Q100 = Q11")
    lines.append("L  X+Q1  Y+Q3 FQ100 M91  ; back to min corner at finish feed")
    lines.append("")

    # Spindle warmup
    lines.append("; ===== Spindle warmup =====")
    lines.append("TOOL CALL 0 Z SQ20")  # Set spindle speed
    lines.append("L  M3")  # Start spindle
    lines.append("Q90 = 1")  # Step counter
    lines.append("LBL 2")  # Spindle warmup loop
    lines.append("  Q20 = Q20 + Q83")  # Increment spindle speed (rpm)
    lines.append("  TOOL CALL 0 Z SQ20")  # Set spindle speed
    lines.append("  FUNCTION DWELL TIME+Q23")  # Dwell (seconds)
    lines.append("  Q90 = Q90 + 1")  # Increment step counter
    lines.append("  FN 12: IF +Q90 LT +Q22 GOTO LBL 2")  # Loop while below step count
    lines.append("  FN 9: IF +Q90 EQU +Q22 GOTO LBL 2")  # End of loop
    lines.append("LBL 0")  # End of spindle warmup loop
    lines.append("")
    lines.append("M5 M9")
    lines.append(f"END PGM {program_name} MM")

    # Block numbering
    numbered_lines = [
        (f"{idx}  {text}" if idx < 10 else f"{idx} {text}")
        for idx, text in enumerate(lines)
    ]
    return "\n".join(numbered_lines) + "\n"


