## Additional performance registers

**Godbolt's registers:** Are not in the Intel documentation for _Broadwell_ and _Skylake_ but seem to work:

|  Event Name   | EventNum:Mask |  Description  | Working |
| :-----------: | :-----------: | :-----------: | :-----------: |
| Early BPU clears | e8:01 | Counts early (normal) Branch Prediction Unit clears: BPU predicted a  taken branch after incorrectly assuming that it was not taken.  The BPU  clear leads to 2 cycle bubble in the Front End. | Yes (?) |
| Late BPU clears | e8:02 | Counts late Branch Prediction Unit clears due to Most Recently Used  conflicts. The BPU clear leads to a 3 cycle bubble in the Front End. | Yes (?) |
| Front-end resteers | e6:1f | Counts the number of times the front end is resteered, mainly when the  Branch Prediction Unit cannot provide a correct prediction and this is  corrected by the Branch Address Calculator at the front end. This can  occur if the code has many branches such that they cannot be consumed by the BPU. Each BACLEAR asserted by the BAC generates approximately an 8  cycle bubble in the instruction fetch pipeline. The effect on total  execution time depends on the surrounding code. | Yes (?) |



Because of that I decided to test several other registers that seem to be relevant to our use case, increased monitoring registers would allow us more precise tests, these are the tested performance registers:

|  Event Name   | EventNum:Mask |  Description  | Working |
| :-----------: | :-----------: | :-----------: | :-----------: |
| BR_MISSP_EXEC | 89:00 | Mispredicted branch instructions executed |     No     |
| BR_BAC_MISSP_EXEC | 8a:00 |   Branch instructions mispredicted at decoding   |      No      |
| BR_CND_EXEC | 8b:00 |   Conditional branch instructions executed   |      No      |
| BR_INST_RETIRED.ALL_BRANCHES | c4:00 | Branch instructions at retirement | Yes |
| BR_INST_RETIRED.CONDITIONAL | c4:01 | Counts the number of conditional branch instructions retired | Yes |
| BR_INST_RETIRED.NOT_TAKEN | c4:10 | Counts the number of not taken branch instructions retired | Yes |
| BR_INST_RETIRED.NEAR_TAKEN | c4:20 | Number of near taken branches retired | Yes |
| BR_MISP_RETIRED.ALL_BRANCHES | c5:00 | Mispredicted branch instructions at retirement [Seems to be only conditional?] | Yes |
| BR_MISP_RETIRED.CONDITIONAL | c5:01 | Mispredicted conditional branch instructions retired | Yes |
| BR_MISP_RETIRED.ALL_BRANCHES | c5:04 | Mispredicted ~~macro~~ [all] branch instructions retired | Yes |
| BR_INST_EXEC.NONTAKEN | 88:40 | Qualify non-taken near branches executed. <br/>Applicable to umask 01H only. | Yes |
| BR_INST_EXEC.TAKEN | 88:80 | Qualify taken near branches executed. Must combine with 01H, 02H, 04H, 08H, 10H, 20H | Yes |
| BTB_Misses | e2:00 | Number of branches the BTB did not produce a prediction | No |
| Br_Bogus | e4:00 | Number of bogus branches. | No (?) |
| BAClears | e6:00 | Number of BAClears asserted. | No |

We only need to consider near branches as they are all done in the same segment. Info about the different terminology (near, far, macro branches): https://software.intel.com/en-us/forums/intel-vtune-amplifier/topic/531087

There seem to be a few new registers that we can use and that should allow us to have a better insight on the BPU.



- ~~`BrMispred` (207): _Number of mispredicted branches retired._~~ 
	~~Always returns that 0 or 1 branch was mispredicted even when testing thousands... assuming it only counts conditional jumps~~
- ~~`BrTaken`(201): _Number of branch instructions retired._~~
	~~Confirms that our `nasm` code works, correct nb read each time~~
- ~~`BrBogus` (502): _Number of bogus branches._~~ 
	~~Could not produce a BTB entry from a non branch instruction. Always 0, possibly working~~
- ~~`BtbMiss` (501): _Number of branches for which the BTB did not produce a prediction._~~
	~~Always 0 even when several resteers, not working~~
- ~~`BaClears` (503): _Number of times BACLEAR is asserted. This is the number of times that a static branch prediction was made, in which the branch decoder decided to make a branch prediction because the BTB did not._~~
	~~always 0, not working~~

## Tests for performance registers

**BaClears**
Some basic jumps: conditional or not and forward or backwards jumps. If a static branch prediction was used, we would see some specific behavior like:
    - Conditional branches never taken
        - Conditional branches always taken
        - Backward branches (loops) will always be taken
        - Forward branches will not be taken

None of this seems to happen and not static branch is detected by the specific counter -> it is not working/present in my CPU.



**BtbMiss**
We would expect some initial misses from the BTB after a boot when the BTB is empty or at least when experiencing several resteers, this is not the case -> performance counter not working/present.



**BrTaken**
The displayed number corresponds to the nb of branches we are running and it is also the case when we include two jumps in the nasm macro.



**BrMispred**
Provides results that are not 0 and consistent between reruns so it seems to be fine.



**BrBogus**
Mix of branch instructions as well as other non-branch related instructions, could not find non-zero values.



**Not specified registers**

A mix of taken, not taken conditional branches as well as some unconditional ones in order to cover most cases where the registers should differ and we are able to see if they work or not.

## Reset of BTB

Can be found in the file `btb_reset.py` which consists of several branches aligned a bit differently and some internal small branches in order to change the content of the BTB.

For the final results, I would recommend rebooting the machine between runs to make sure that we have an empty BTB even though the reset function seems to work quite well (more consistent results).