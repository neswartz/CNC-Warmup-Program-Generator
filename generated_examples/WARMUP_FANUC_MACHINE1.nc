%
O0001 (WARMUP_FANUC_MACHINE1)
(FANUC 31I • UNITS: MM • Machine 1)

(===== CONFIG: MACHINE LIMITS IN MACHINE COORDS (G53) =====)
#100 = -381     (X_MIN_SAFE)
#101 = 381     (X_MAX_SAFE)
#102 = -254     (Y_MIN_SAFE)
#103 = 254     (Y_MAX_SAFE)
#104 = 0      (Z_HOME)
#106 = -50     (Z_TOP_SAFE)
#107 = -500     (Z_BOTTOM_SAFE)

(===== CONFIG: AXIS FEED RAMP =====)
#120 = 1000     (FEED_START  mm/min)
#121 = 2000     (FEED_FIN    mm/min)
#122 = 4     (FEED_STEPS)

(===== CONFIG: SPINDLE WARMUP =====)
#200 = 500    (RPM_START)
#201 = 6000    (RPM_FIN)
#202 = 5    (RPM_STEPS   >=2)
#203 = 60    (DWELL PER STEP, seconds)

(===== HOUSEKEEPING / SAFE START =====)
G21 G17 G90 G94 G40 G49 G80
M05
M09
M08                  (optional coolant)

IF[#202 LT 2.] THEN #202 = 2.

#123 = [#121 - #120] / [#122 - 1.]    (axis feed delta per step)
#205 = [#201 - #200] / [#202 - 1.]    (spindle rpm delta per step)

(----- Establish safe machine positions -----)
G90 G53 G00 Z#104            (park at Z home)

G90 G53 G00 Z#106            (down to top-safe Z)
#110 = [#100 + #101] / 2.    (center X)
#111 = [#102 + #103] / 2.    (center Y)
G90 G53 G00 X#110 Y#111      (move to XY center)

(============ Z WARMUP ============)
#150 = ABS[#106 - #107]      (positive stroke length)
G91                          (incremental moves around the safe center)
#130 = 1.
WHILE[#130 LE #122] DO1
  #131 = #120 + [#123 * [#130 - 1.]]    (current feed)
  G01 Z[-#150] F#131                    (down to bottom-safe relative to top-safe)
  G01 Z[#150]  F#131                    (back up to top-safe)
  #130 = #130 + 1.
END1

(============ XY WARMUP ============)
#160 = [#101 - #100]         (rect width)
#161 = [#103 - #102]         (rect height)
#162 = #160 / 2.             (half width)
#163 = #161 / 2.             (half height)

#140 = 1.
WHILE[#140 LE #122] DO2
  #141 = #120 + [#123 * [#140 - 1.]]    (current feed)

  (center -> corner A)
  G01 X[-#162] Y[-#163] F#141
  (A -> corner C (opposite))
  G01 X[#160]  Y[#161]  F#141
  (C -> A)
  G01 X[-#160] Y[-#161] F#141
  (A -> C again (second traverse per step))
  G01 X[#160]  Y[#161]  F#141
  (return to center)
  G01 X[-#162] Y[-#163] F#141

  #140 = #140 + 1.
END2

(============ SPINDLE WARMUP ============)
G90
#210 = 1.
WHILE[#210 LE #202] DO3
  #211 = FIX[#200 + [#205 * [#210 - 1.]]] (target RPM)
  IF[#210 EQ 1.] THEN
    S#211 M03
  ELSE
    S#211
  ENDIF
  G04 X#203 (dwell time)
  #210 = #210 + 1.
END3
M05
M09

(============ PARK ============)
G90 G53 G00 Z#104
M30
%
