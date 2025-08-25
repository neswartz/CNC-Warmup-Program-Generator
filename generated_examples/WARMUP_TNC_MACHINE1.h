0  BEGIN PGM WARMUP_TNC_MACHINE1 MM
1  ; MACHINE: Machine 1
2  ; ===== Config =====
3  Q1 =      0    ; X_MIN_SAFE (mm)
4  Q2 =    762    ; X_MAX_SAFE
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
24 M8
25 Q80 = +Q11 - Q10        ; FEED_RANGE
26 Q81 = Q80/3             ; FEED_INC
27 Q83 = (Q21 - Q20)/Q22   ; RPM_INC
28 
29 L  Z+Q5 FMAX M91  ; to safe Z
30 ; ===== Z axis test: top -> bottom -> top with increasing feed from start to finish =====
31 Q100 = Q10
32 L  Z+Q6 FQ100 M91        ; to Z bottom at start feed
33 Q100 = Q10 + Q81
34 L  Z+Q5 FQ100 M91        ; back to Z top at start+1/3 range
35 Q100 = Q10 + Q81*2
36 L  Z+Q6 FQ100 M91        ; to Z bottom at start+2/3 range
37 Q100 = Q11
38 L  Z+Q5 FQ100 M91        ; back to Z top at finish feed
39 
40 ; ===== XY axis test: min -> max -> min with increasing feed from start to finish =====
41 L  Z+Q5 FMAX M91         ; ensure safe Z for XY motion
42 L  X+Q1  Y+Q3 FQ10 M91   ; go to min corner (0,0) with start feed
43 Q100 = Q10
44 L  X+Q2  Y+Q4 FQ100 M91  ; to max corner at start feed
45 Q100 = Q10 + Q81
46 L  X+Q1  Y+Q3 FQ100 M91  ; back to min corner at start+1/3 range
47 Q100 = Q10 + Q81*2
48 L  X+Q2  Y+Q4 FQ100 M91  ; to max corner at start+2/3 range
49 Q100 = Q11
50 L  X+Q1  Y+Q3 FQ100 M91  ; back to min corner at finish feed
51 
52 ; ===== Spindle warmup =====
53 TOOL CALL 0 Z SQ20
54 L  M3
55 Q90 = 1
56 LBL 2
57   Q20 = Q20 + Q83
58   TOOL CALL 0 Z SQ20
59   FUNCTION DWELL TIME+Q23
60   Q90 = Q90 + 1
61   FN 12: IF +Q90 LT +Q22 GOTO LBL 2
62   FN 9: IF +Q90 EQU +Q22 GOTO LBL 2
63 LBL 0
64 
65 M5 M9
66 END PGM WARMUP_TNC_MACHINE1 MM
