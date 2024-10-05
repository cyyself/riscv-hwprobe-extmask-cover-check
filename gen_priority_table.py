#!/usr/bin/env python3

import json

ext_bitmask_dict = {}
ext_bitmask = []
hwprobe = []

def load_json():
    global ext_bitmask_dict, ext_bitmask, hwprobe
    with open('info/ext_bitmask.json', 'r') as f:
        ext_bitmask_dict = json.load(f)['ext_bitmask']
        ext_bitmask = ext_bitmask_dict.values()
    with open('info/hwprobe.json', 'r') as f:
        hwprobe = json.load(f)['hwprobe']

def gen_riscv_ext_bitmask_table():
    tmp = []
    for k, v in ext_bitmask_dict.items():
        idx_hwprobe = 0
        if v in hwprobe:
            idx_hwprobe = hwprobe.index(v)
        else:
            if v == 'i':
                idx_hwprobe = -4
            elif v == 'm':
                idx_hwprobe = -3
            elif v == 'a':
                idx_hwprobe = -2
        tmp.append((idx_hwprobe, v, k))
    tmp = sorted(tmp)
    max_len = max([len(i[1]) for i in tmp])
    for i in tmp:
        space_append = ' ' * (max_len + 1 - len(i[1]))
        print(f'    {{"{i[1]}",{space_append}{int(i[2])//64}, {int(i[2])%64:2d}}},')

load_json()
gen_riscv_ext_bitmask_table()
