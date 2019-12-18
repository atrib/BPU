#!/usr/bin/env python

import os
import subprocess
import sys

from lib.agner import *

def reset(name, num_branches, align):
    code = """
%macro OneJump 0
mov ecx,0
%%loop1:
jmp %%next
align {align}
%%next:
inc ecx
align 4
cmp ecx, 10
jne %%loop1
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
    r = run_test(code, [1], repetitions=3)
    return

def add_tests(agner):
    nums = range(512, 5500, 512) #range(512, 5500 , 512)
    aligns = [2**x for x in range(0, 3)]

    for num in nums:
        for align in aligns:
            reset("reset", num, align)
    print("reset done")
