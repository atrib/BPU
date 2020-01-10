#!/usr/bin/env python

import os
import subprocess
import sys

from lib.agner import *

def my_avg(list, register):
    n = 0
    sum = 0.0
    for elem in list:
        sum += elem.get(register)
        n += 1
    return sum/n

def avg_dict(list):
    avgDict = {}

    avgDict['BaClrAny'] = my_avg(list, 'BaClrAny')
    avgDict['totBr'] = my_avg(list, 'totBr')
    avgDict['BrCondTkn'] = my_avg(list, 'BrCondTkn')
    avgDict['BrMispred'] = my_avg(list, 'BrMispred')

    return avgDict
    

def btb_size_test(name, num_branches, align):
    test_code = """
align 1024

mov ecx, 2
mov edx, 2
nop
align {align}/2
next1:
%rep {align}/2
nop
%endrep

nop
nop
jmp next2
align {align}/2
next2:
%rep {align}/2
nop
%endrep

nop
nop
jmp next3
align {align}/2
next3:
align {align}/2

nop
nop
jmp next4
align {align}/2
next4:
align {align}/2

nop
nop
jmp next5
align {align}/2
next5:
align {align}/2

nop
nop
jmp next6
align {align}/2
next6:
%rep {align}/16
nop
%endrep


loop: dec ecx
cmp ecx, 0
jne next2

dec edx
inc ecx
cmp edx, 0
jne next1


%rep 64
nop
%endrep
""".format(num_branches=num_branches, align=align)
    r = run_test(test_code, [207, 410, 502, 501], repetitions=100)
    return avg_dict(r)


def plot(xs, ys, result, name, index):
    import numpy as np
    import matplotlib.pyplot as plt
    plt.style.use('custom')

    if index:
        ax = plt.subplot(2, 2, index)
        plt.tight_layout()
    else:
        ax = plt.subplot(1, 1, 1)
    ax.set_yscale('log', basey=2)
    plt.title(name)

    plt.xlabel("Branch count")
    plt.ylabel("Branch alignment")
    ax.xaxis.set_ticks(xs)
    xs = np.array(xs + [xs[-1] + 1])
    ys = np.array(ys + [ys[-1] * 2])
    xx, yy = np.meshgrid(xs, ys)
    result = np.array(result)
    plt.pcolor(xx, yy, result, cmap='jet')
    plt.xticks(rotation='vertical')
    plt.colorbar()


def btb_test(nums, aligns, name):
    resteer = []
    early = []
    late = []
    core = []
    for align in aligns:
        resteer.append([])
        early.append([])
        late.append([])
        core.append([])
        for num in nums:
            res = btb_size_test("BTB size test %d branches aligned on %d" % (num, align), num, align)
            exp = 100 #num * 100.0 # number of branches under test

            print("Number of resteers:", res['BaClrAny'] / 100)
            print("Number of total branches:", res['totBr'] / 100 -1) #initial jmp from agner tools
            print("Number of conditional branches:", res['BrCondTkn'] / 100 -1)
            print("Mispredicted conditional branches:", res['BrMispred'] / 100)

            resteer[-1].append(res['BaClrAny'] / exp)
            early[-1].append(res['totBr'] / exp)
            late[-1].append(res['BrCondTkn'] / exp)
            core[-1].append(res['BrMispred'] / exp) # percent of mispredicted branches
    return {'resteer': resteer, 'totBr': early, 'BrCondTkn': late, 'mispred': core}


def btb_plot(nums, aligns, name, results, alt):
    import matplotlib.pyplot as plt
    fig = plt.figure()
    locs, labels = plt.xticks()
    plt.setp(labels, rotation=90)
    plt.title(name)
    fig.suptitle(name, fontsize=6)
    if alt:
        plot(nums, aligns, 100*results['resteer'], "Front-end re-steers", 0)
    else:
        plot(nums, aligns, results['resteer'], "Front-end re-steers", 1)
        plot(nums, aligns, results['totBr'], "Total branch instr", 2)
        plot(nums, aligns, results['BrCondTkn'], "Total conditional branches", 3)
        plot(nums, aligns, results['mispred'], "Mispredicted conditional branches", 4)


def add_test(agner, nums, aligns, name):
    test = lambda: btb_test(nums, aligns, name)
    plot = lambda results, alt : btb_plot(nums, aligns, name, results, alt)
    agner.add_test(name, test, plot)


def add_tests(agner):
    # attempt to find the number of ways of the BTB
    add_test(agner, [6], [2**x for x in range(15, 16)], "Eviction set with unconditional direct branches")
