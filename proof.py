#!/usr/bin/env python3

import json
from queue import Queue

ext_bitmask = []
ext_bitmask_child = {}
ext_bitmask_in_degree = {}
hwprobe = []
riscv_isa_imply = []

def load_json():
    global ext_bitmask, hwprobe, riscv_isa_imply, ext_bitmask_child
    with open('info/ext_bitmask.json', 'r') as f:
        ext_bitmask = json.load(f)['ext_bitmask']
    with open('info/hwprobe.json', 'r') as f:
        hwprobe = json.load(f)['hwprobe']
    with open('info/riscv_isa_imply.json', 'r') as f:
        riscv_isa_imply = json.load(f)['riscv_isa_imply']
    for k, v in riscv_isa_imply:
        # Add child node to the child dict
        if k not in ext_bitmask_child:
            ext_bitmask_child[k] = []
        ext_bitmask_child[k] += [v]

def get_reachable_isa(isa):
    reachable_isa = set()
    reachable_isa.add(isa)
    q = Queue()
    q.put(isa)
    while not q.empty():
        cur = q.get()
        if cur in ext_bitmask_child:
            for c in ext_bitmask_child[cur]:
                if c not in reachable_isa:
                    reachable_isa.add(c)
                    q.put(c)
    return reachable_isa

def isa_imply_is_dag():
    # Using Topological Sort to check if riscv_isa_imply is a DAG
    in_degree = {}
    for k, v in riscv_isa_imply:
        # Create all node as key in in_degree, thus we can check if
        # there is any node with in_degree 0
        if k not in in_degree:
            in_degree[k] = 0
        if v not in in_degree:
            in_degree[v] = 0
        # Increase in_degree of the ext_bitmask_child node
        in_degree[v] += 1
    q = Queue()
    # Add all node with in_degree 0 to the queue
    for k, v in in_degree.items():
        if v == 0:
            q.put(k)
    # Topological Sort BFS
    while not q.empty():
        cur = q.get()
        if cur in ext_bitmask_child:
            for c in ext_bitmask_child[cur]:
                in_degree[c] -= 1
                if in_degree[c] == 0:
                    q.put(c)
    # If all node has in_degree 0 after TopoSort, then it is a DAG
    return all([v == 0 for v in in_degree.values()])

def ext_bitmask_is_subset_of_hwprobe():
    ext_bitmask_set = set(ext_bitmask)
    hwprobe_set = set(hwprobe).union(set(['i', 'm', 'a']))
    return ext_bitmask_set.issubset(hwprobe_set)

def is_safe_to_use_ext_bitmask_seq():
    # Make sure we can use the ISA extension sequence in ext_bitmask
    # to generate the minimal cover of ISA bitmask used in hwprobe.
    hwprobe_ptr = 0
    ext_bitmask_ptr = 0
    hwprobe_seen = set(['i', 'm', 'a'])
    ext_bitmask_seen = set()
    ext_bitmask_cover = set()
    while ext_bitmask_ptr < len(ext_bitmask):
        # Update ext_bitmask_cover
        ext_bitmask_seen.add(ext_bitmask[ext_bitmask_ptr])
        ext_bitmask_cover.add(ext_bitmask[ext_bitmask_ptr])
        # Query hwprobe seen
        if ext_bitmask[ext_bitmask_ptr] in hwprobe: # Skip i, m, a
            ext_index_in_hwprobe = hwprobe.index(ext_bitmask[ext_bitmask_ptr])
            if hwprobe_ptr <= ext_index_in_hwprobe:
                for i in range(hwprobe_ptr, ext_index_in_hwprobe + 1):
                    hwprobe_seen.add(hwprobe[i])
                hwprobe_ptr = ext_index_in_hwprobe + 1
        # Check if there is any new cover that already seen in hwprobe but not in ext_bitmask_seen
        new_cover = ext_bitmask_cover.union(get_reachable_isa(ext_bitmask[ext_bitmask_ptr])) - ext_bitmask_cover
        for c in new_cover:
            if c in hwprobe_seen and c not in ext_bitmask_seen:
                print(f"New cover {c} is not in ext_bitmask_seen when processing {ext_bitmask[ext_bitmask_ptr]}")
                print(hwprobe_seen)
                print(ext_bitmask_seen)
                return False
        ext_bitmask_ptr += 1
    return True

load_json()
assert isa_imply_is_dag(), "riscv_isa_imply is not a DAG"
assert ext_bitmask_is_subset_of_hwprobe(), "ext_bitmask is not subset of hwprobe"
assert is_safe_to_use_ext_bitmask_seq(), "ext_bitmask sequence is not safe to use"
exit(0)