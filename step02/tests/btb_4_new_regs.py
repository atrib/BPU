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

    avgDict['MispCond'] = my_avg(list, 'MispCond')
    avgDict['MispMacro'] = my_avg(list, 'MispMacro')
    avgDict['NTknBrExe'] = my_avg(list, 'NTknBrExe')
    avgDict['TknBrExe'] = my_avg(list, 'TknBrExe')

    return avgDict
    

def btb_size_test(name, num_branches, align):
    test_code = """
%macro OneJump 0
mov ecx,0
%%loop1:
inc ecx
cmp ecx, 10
jne %%loop1
cmp ecx, 25
je %%next2
jmp %%next
align {align}
%%next: jmp %%next2
%%next2:
%endmacro

%rep {num_branches}
OneJump
%endrep

%rep 64
nop
%endrep
""".format(num_branches=num_branches, align=align)
    r = run_test(test_code, [507, 508, 509, 510], repetitions=100)
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
            exp = num * 100.0 # number of branches under test
            resteer[-1].append(res['MispCond'] / 100) # nb per run
            early[-1].append(res['MispMacro'] / 100) # nb per run
            late[-1].append(res['NTknBrExe'] / 100) # nb per run
            core[-1].append(res['TknBrExe'] / 100) # nb per run
    return {'MispCond': resteer, 'MispMacro': early, 'NTknBrExe': late, 'TknBrExe': core}


def btb_plot(nums, aligns, name, results, alt):
    import matplotlib.pyplot as plt
    fig = plt.figure()
    locs, labels = plt.xticks()
    plt.setp(labels, rotation=90)
    plt.title(name)
    fig.canvas.set_window_title(name)
    if alt:
        plot(nums, aligns, results['BaClrAny'], "Resteers", 0)
    else:
        plot(nums, aligns, results['MispCond'], "BR_MISP_RETIRED.CONDITIONAL", 1)
        plot(nums, aligns, results['MispMacro'], "BR_MISP_RETIRED.ALL_BRANCHES", 2)
        plot(nums, aligns, results['NTknBrExe'], "BR_INST_EXEC.NONTAKEN", 3)
        plot(nums, aligns, results['TknBrExe'], "BR_INST_EXEC.TAKEN", 4)


def add_test(agner, nums, aligns, name):
    test = lambda: btb_test(nums, aligns, name)
    plot = lambda results, alt : btb_plot(nums, aligns, name, results, alt)
    agner.add_test(name, test, plot)


def add_tests(agner):
    add_test(agner, range(1, 10), [2**x for x in range(0, 10)], "Test new registers") # not 0
