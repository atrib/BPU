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

    avgDict['BrTaken'] = my_avg(list, 'BrTaken')
    avgDict['BrMispred'] = my_avg(list, 'BrMispred')
    avgDict['BtbMiss'] = my_avg(list, 'BtbMiss')
    avgDict['BaClears'] = my_avg(list, 'BaClears')

    return avgDict
    

def btb_size_test(name, num_branches, align):
    test_code = """
%macro OneJump 0
jmp %%next
align {align}
%%next:
%endmacro

jmp BtbLoop
align 4 * 1024 * 1024; align to a 4MB boundary
BtbLoop:
%rep {num_branches}
OneJump
%endrep

%rep 64
nop
%endrep
""".format(num_branches=num_branches, align=align)
    r = run_test(test_code, [207, 201, 501, 503], repetitions=100)
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
            resteer[-1].append(res['BrTaken'] / 100) # nb per run
            early[-1].append(res['BtbMiss'] / 100) # nb per run
            late[-1].append(res['BaClears'] / 100) # nb per run
            core[-1].append(res['BrMispred'] / 100) # nb per run
    return {'BrTaken': resteer, 'BtbMiss': early, 'BaClears': late, 'mispred': core}


def btb_plot(nums, aligns, name, results, alt):
    import matplotlib.pyplot as plt
    fig = plt.figure()
    locs, labels = plt.xticks()
    plt.setp(labels, rotation=90)
    plt.title(name)
    fig.canvas.set_window_title(name)
    if alt:
        plot(nums, aligns, results['BrTaken'], "Branch instructions taken", 0)
    else:
        plot(nums, aligns, results['BrTaken'], "Branch instructions taken", 1)
        plot(nums, aligns, results['BtbMiss'], "BTB misses", 2)
        plot(nums, aligns, results['BaClears'], "Nb of Static predictions, not BTB", 3)
        plot(nums, aligns, results['mispred'], "Nb of Mispredicted branches", 4)


def add_test(agner, nums, aligns, name):
    test = lambda: btb_test(nums, aligns, name)
    plot = lambda results, alt : btb_plot(nums, aligns, name, results, alt)
    agner.add_test(name, test, plot)


def add_tests(agner):
    # attempt to find total size
    #add_test(agner, range(512, 9000, 512), [1, 2, 4, 8, 16, 32, 64], "Total size") # not 0
    add_test(agner, range(512, 9000 , 512), [2**x for x in range(0, 6)], "Total size") # not 0

    # attempt to find set bits
    #add_test(agner, [3, 4, 5], [2**x for x in range(0, 24)],  "Bits in set") # 1 -> 0

    # attempt to find number of ways : large leaps to ensure we hit the same set every time
    #add_test(agner, range(1,12), [2**x for x in range(0, 21)], "Number of ways") # 1 -> 0

    # attempt to find number of addr bits : two branches very spread
    #add_test(agner, [2], [2**x for x in range(6, 28)], "Number of address bits for set")

    # attempt to find number of addr bits : two branches very spread
    #add_test(agner, [3, 4, 5], [2**x for x in range(6, 28)], "Number of address bits for set")
