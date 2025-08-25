0  BEGIN PGM WARMUP_TNC_MACHINE3 MM
1  ; MACHINE: Machine 3
2  ; ===== Config =====
3  Q1 =      0    ; X_MIN_SAFE (mm)
4  Q2 =   1270    ; X_MAX_SAFE
5  Q3 =      0    ; Y_MIN_SAFE
6  Q4 =    508    ; Y_MAX_SAFE
7  Q5 =      0    ; Z_TOP_SAFE
8  Q6 =   -500    ; Z_BOTTOM_SAFE
9  
10 Q10 =   1000    ; FEED_START (mm/min)
11 Q11 =   2000    ; FEED_FIN
12 
13 Q20 =    500    ; RPM_START
14 Q21 =   6000    ; RPM_FIN
15 Q22 =      5    ; RPM_STEPS
16 Q23 =     60    ; DWELL PER STEP (s)
17 
18 ; ===== Safe start =====
19 M5 M9
20 PLANE RESET
21 TRANS DATUM RESET
22 FUNCTION RESET TCPM
23 TOOL CALL 0 Z
24 Q80 = +Q11 - Q10        ; FEED_RANGE
25 Q81 = Q80/3             ; FEED_INC
26 Q83 = (Q21 - Q20)/Q22   ; RPM_INC
27 
28 L  Z+Q5 FMAX M91  ; to safe Z
29 ; ===== Z axis test: top -> bottom -> top with increasing feed from start to finish =====
30 Q100 = Q10
31 L  Z+Q6 FQ100 M91        ; to Z bottom at start feed
32 Q100 = Q10 + Q81
33 L  Z+Q5 FQ100 M91        ; back to Z top at start+1/3 range
34 Q100 = Q10 + Q81*2
35 L  Z+Q6 FQ100 M91        ; to Z bottom at start+2/3 range
36 Q100 = Q11
37 L  Z+Q5 FQ100 M91        ; back to Z top at finish feed
38 
39 ; ===== XY axis test: min -> max -> min with increasing feed from start to finish =====
40 L  Z+Q5 FMAX M91         ; ensure safe Z for XY motion
41 L  X+Q1  Y+Q3 FQ10 M91   ; go to min corner (0,0) with start feed
42 Q100 = Q10
43 L  X+Q2  Y+Q4 FQ100 M91  ; to max corner at start feed
44 Q100 = Q10 + Q81
45 L  X+Q1  Y+Q3 FQ100 M91  ; back to min corner at start+1/3 range
46 Q100 = Q10 + Q81*2
47 L  X+Q2  Y+Q4 FQ100 M91  ; to max corner at start+2/3 range
48 Q100 = Q11
49 L  X+Q1  Y+Q3 FQ100 M91  ; back to min corner at finish feed
50 
51 ; ===== Spindle warmup =====
52 TOOL CALL 0 Z SQ20
53 L  M3
54 Q90 = 1
55 LBL 2
56   Q20 = Q20 + Q83
57   TOOL CALL 0 Z SQ20
58   FUNCTION DWELL TIME+Q23
59   Q90 = Q90 + 1
60   FN 12: IF +Q90 LT +Q22 GOTO LBL 2
61   FN 9: IF +Q90 EQU +Q22 GOTO LBL 2
62 LBL 0
63 
64 M5 M9
65 END PGM WARMUP_TNC_MACHINE3 MM
