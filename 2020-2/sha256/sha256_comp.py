#!/usr/bin/env python3

mp_ori, mp_new = {}, {}

def parse(f):
    mode = 0
    for line in f.readlines():
        if line[:10] == "// Feynman" or line[:11] == "// Original":
            continue
        if line[:2] != "//":
            return
        elif line.split()[1] == "Result":
            mode = 1
        else:
            circ, val = line.strip().split()[1][:-1], int(line.strip().split()[2])
            if circ not in mp_ori:
                mp_ori[circ] = 0
            if circ not in mp_new:
                mp_new[circ] = 0
            if mode:
                mp_new[circ] += val
            else:
                mp_ori[circ] += val
        
for options in ["tpar", "cnotmin"]:
    mp_ori.clear()
    mp_new.clear()
    for num in range(1, 65):
        with open(f"./sha256/{options}/sha256-qasm-{num:#02d}-{options}.qasm", "r") as f:
            parse(f)
    print(f"Feynopt : -{options} -simplify")
    for k, v in mp_ori.items():
        print(k, v, mp_new[k], sep='\t')


