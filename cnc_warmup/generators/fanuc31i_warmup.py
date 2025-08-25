from typing import List

"""

Fanuc 31i warmup program generator.

This module produces a G53 (machine coordinates) macro-style warmup program that
exercises Z and XY axes and performs a spindle warmup using WHILE loops with
configurable steps and dwell times.

Notes:
Warmup is done from the center of the machine using G53 to reference absolute positions.

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

    clamped_steps = max(2, int(steps))
    clamped_dwell = max(0, int(seconds_per_step))

    max_x = abs(float(x_travel))
    max_y = abs(float(y_travel))
    max_z = abs(float(z_travel))

    # Machine limits defaults (centered X/Y around 0; Z home at 0)
    half_x = max_x / 2.0
    half_y = max_y / 2.0
    x_min_safe = -half_x
    x_max_safe = +half_x
    y_min_safe = -half_y
    y_max_safe = +half_y
    z_home = 0.0
    # Choose a reasonable top-safe slightly below home: 10% of travel capped at 50mm
    z_top_safe = -min(max_z * 0.10, 50.0)
    z_bottom_safe = -max_z

    # Feed steps for axis exercises (template uses a separate count).
    # We default to 4 passes; user can edit in the output program.
    clamped_feed_steps = 4

    lines: List[str] = []
    lines.append("%")
    lines.append("O0001 (" + str(program_name).upper() + ")")
    if machine_label:
        lines.append("(FANUC 31I \u2022 UNITS: MM \u2022 " + machine_label + ")")
    else:
        lines.append("(FANUC 31I \u2022 UNITS: MM)")
    lines.append("")

    # Config: machine limits
    lines.append("(===== CONFIG: MACHINE LIMITS IN MACHINE COORDS (G53) =====)")
    lines.append(f"#100 = {_format_number(x_min_safe)}     (X_MIN_SAFE)")
    lines.append(f"#101 = {_format_number(x_max_safe)}     (X_MAX_SAFE)")
    lines.append(f"#102 = {_format_number(y_min_safe)}     (Y_MIN_SAFE)")
    lines.append(f"#103 = {_format_number(y_max_safe)}     (Y_MAX_SAFE)")
    lines.append(f"#104 = {_format_number(z_home)}      (Z_HOME)")
    lines.append(f"#106 = {_format_number(z_top_safe)}     (Z_TOP_SAFE)")
    lines.append(f"#107 = {_format_number(z_bottom_safe)}     (Z_BOTTOM_SAFE)")
    lines.append("")

    # Config: axis feed ramp
    lines.append("(===== CONFIG: AXIS FEED RAMP =====)")
    lines.append(f"#120 = {_format_number(start_feed_mm_min)}     (FEED_START  mm/min)")
    lines.append(f"#121 = {_format_number(finish_feed_mm_min)}     (FEED_FIN    mm/min)")
    lines.append(f"#122 = 4     (FEED_STEPS)")
    lines.append("")

    # Config: spindle warmup
    lines.append("(===== CONFIG: SPINDLE WARMUP =====)")
    lines.append(f"#200 = {_format_number(start_rpm)}    (RPM_START)")
    lines.append(f"#201 = {_format_number(finish_rpm)}    (RPM_FIN)")
    lines.append(f"#202 = {_format_number(clamped_steps)}    (RPM_STEPS   >=2)")
    lines.append(f"#203 = {_format_number(clamped_dwell)}    (DWELL PER STEP, seconds)")
    lines.append("")

    # Housekeeping / safe start
    lines.append("(===== HOUSEKEEPING / SAFE START =====)")
    lines.append("G21 G17 G90 G94 G40 G49 G80")
    lines.append("M05")
    lines.append("M09")
    if include_coolant:
        lines.append("M08                  (optional coolant)")
    lines.append("")

    # Ensure step counts sane
    lines.append("IF[#202 LT 2.] THEN #202 = 2.")
    lines.append("")

    # Precompute step sizes
    lines.append("#123 = [#121 - #120] / [#122 - 1.]    (axis feed delta per step)")
    lines.append("#205 = [#201 - #200] / [#202 - 1.]    (spindle rpm delta per step)")
    lines.append("")

    # Go to safe machine Z before XY motion
    lines.append("(----- Establish safe machine positions -----)")
    lines.append("G90 G53 G00 Z#104            (park at Z home)")
    lines.append("")
    # Move to Z top-safe and XY center
    lines.append("G90 G53 G00 Z#106            (down to top-safe Z)")
    lines.append("#110 = [#100 + #101] / 2.    (center X)")
    lines.append("#111 = [#102 + #103] / 2.    (center Y)")
    lines.append("G90 G53 G00 X#110 Y#111      (move to XY center)")
    lines.append("")

    # Z warmup
    lines.append("(============ Z WARMUP ============)")
    lines.append("#150 = ABS[#106 - #107]      (positive stroke length)")
    lines.append("G91                          (incremental moves around the safe center)")
    lines.append("#130 = 1.")
    lines.append("WHILE[#130 LE #122] DO1")
    lines.append("  #131 = #120 + [#123 * [#130 - 1.]]    (current feed)")
    lines.append("  G01 Z[-#150] F#131                    (down to bottom-safe relative to top-safe)")
    lines.append("  G01 Z[#150]  F#131                    (back up to top-safe)")
    lines.append("  #130 = #130 + 1.")
    lines.append("END1")
    lines.append("")

    # XY warmup
    lines.append("(============ XY WARMUP ============)")

    lines.append("#160 = [#101 - #100]         (rect width)")
    lines.append("#161 = [#103 - #102]         (rect height)")
    lines.append("#162 = #160 / 2.             (half width)")
    lines.append("#163 = #161 / 2.             (half height)")
    lines.append("")
    lines.append("#140 = 1.")
    lines.append("WHILE[#140 LE #122] DO2")
    lines.append("  #141 = #120 + [#123 * [#140 - 1.]]    (current feed)")
    lines.append("")
    lines.append("  (center -> corner A)")
    lines.append("  G01 X[-#162] Y[-#163] F#141")
    lines.append("  (A -> corner C (opposite))")
    lines.append("  G01 X[#160]  Y[#161]  F#141")
    lines.append("  (C -> A)")
    lines.append("  G01 X[-#160] Y[-#161] F#141")
    lines.append("  (A -> C again (second traverse per step))")
    lines.append("  G01 X[#160]  Y[#161]  F#141")
    lines.append("  (return to center)")
    lines.append("  G01 X[-#162] Y[-#163] F#141")
    lines.append("")
    lines.append("  #140 = #140 + 1.")
    lines.append("END2")
    lines.append("")


    # Spindle warmup loop
    lines.append("(============ SPINDLE WARMUP ============)")
    lines.append("G90")
    lines.append("#210 = 1.")
    lines.append("WHILE[#210 LE #202] DO3")
    lines.append("  #211 = FIX[#200 + [#205 * [#210 - 1.]]] (target RPM)")
    lines.append("  IF[#210 EQ 1.] THEN")
    lines.append("    S#211 M03")
    lines.append("  ELSE")
    lines.append("    S#211")
    lines.append("  ENDIF")
    lines.append("  G04 X#203 (dwell time)")
    lines.append("  #210 = #210 + 1.")
    lines.append("END3")
    lines.append("M05")
    if include_coolant:
        lines.append("M09")
    lines.append("")

    # Park
    lines.append("(============ PARK ============)")
    lines.append("G90 G53 G00 Z#104")
    lines.append("M30")
    lines.append("%")

    return "\n".join(lines) + "\n"



