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

    #avgDict['BrTaken'] = my_avg(list, 'BrTaken')
    avgDict['BaClrAny'] = my_avg(list, 'BaClrAny')
    avgDict['BaClrEly'] = my_avg(list, 'BaClrEly')
    avgDict['BaClrL8'] = my_avg(list, 'BaClrL8')
    avgDict['BrMispred'] = my_avg(list, 'BrMispred')

    return avgDict
    

def btb_loop_test(name, num_branches, align):
    test_code = """
%macro OneJump 0
mov ecx,0
%%loop1:
inc ecx
cmp ecx, 25
jne %%loop1
cmp ecx, 25
je %%next
align {align}
%%next:
%endmacro

%rep {num_branches}
OneJump
%endrep

%rep 64
nop
%endrep
""".format(num_branches=num_branches, align=align)
    #r = run_test(test_code, [207, 201, 403, 404], repetitions=100)
    r = run_test(test_code, [207, 410, 403, 404], repetitions=100)
    return avg_dict(r)

def btb_size_test(name, num_branches, align):
    test_code = """
%macro OneJump 0
jmp %%next
align {align}
%%next:
%endmacro

%rep {num_branches}
OneJump
%endrep

%rep 64
nop
%endrep
""".format(num_branches=num_branches, align=align)
    r = run_test(test_code, [207, 201, 403, 404], repetitions=100)
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
            print("Running nb_branches=", num, "and alignment=", align)
            res = btb_loop_test("BTB loop test %d branches aligned on %d" % (num, align), num, align)
            exp = num * 100.0 * 26 # number of branches under test

            #res = btb_size_test("BTB loop test %d branches aligned on %d" % (num, align), num, align)
            #exp = num * 100.0  # number of branches under test

            #resteer[-1].append(res['BrTaken'] / 100)
            resteer[-1].append(res['BaClrAny'] / exp)
            early[-1].append(res['BaClrEly'] / exp)
            late[-1].append(res['BaClrL8'] / exp)
            core[-1].append(res['BrMispred'] / exp)
    return {'resteer': resteer, 'early': early, 'late': late, 'mispred': core}


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
        #plot(nums, aligns, results['resteer'], "Nb branch taken", 1)
        plot(nums, aligns, results['early'], "Early clears in [0,1]", 2)
        plot(nums, aligns, results['late'], "Late clears in [0,1]", 3)
        plot(nums, aligns, results['mispred'], "Nb mispredicted Branches", 4)


def add_test(agner, nums, aligns, name):
    test = lambda: btb_test(nums, aligns, name)
    plot = lambda results, alt : btb_plot(nums, aligns, name, results, alt)
    agner.add_test(name, test, plot)


def add_tests(agner):
    add_test(agner, range(1,12), [2**x for x in range(0, 14)], "Loop test")
