## Conditional branches

**Conditional loops and unconditional branches**

Can be found in the `btb_loops.py` file.
We keep the unconditional branches from the original tests but we add a backward loop to it:

```pseudocode
start: counter = 0
   br to unconditional
   NOP
   NOP
   ... to create the alignment
   NOP
   NOP
unconditional: counter++
    if counter != 25 branch to start
```

We will be repeating our forward unconditional jump which should have no effect on the BTB as is already in the cache after the first time.
The backwards loop will be repeated 25 times which brings the number of jumps per iteration to 50.

We are expecting that the BPU contains a loop branch predictor which handles on its own the loop branches without affecting the BTB too much.
Here is how it affects the monitored registers:

- The amount of mispredicted branches increases: from 0.2%-1% to 0.5%-3%. The most significant change can be observed for an alignment of 2^8 and above where the misprediction rate is around 2%. The effect of the increasing branch count (decreasing the misprediciton rate) can no longer be observed.

- The front-end resteers seem unaffected by the branch loops except for the fact that the percentage is lower. This can be explained by the fact that only our initial unconditional branches cause a resteer but out newly added loop branches do not so we only have a resteer on the first unconditional branch, the following will result in a BTB hit and thus a correct result.

- For the early clears, we have roughly 40-50% for an alignment of 2^3 or below which we can assume is caused by the fact that we now have 50% of the branches that are loop branches which result in higher rate of early clears. For the nb of sequential branches 1 and 2, there was previously a 100% early clear rate which drops to 0 if the branch alignment is higher than 2^4, I do not know how to explain this.
    Additionally, why are there ealry clears in the initial version as there are only unconditional branches, there should not be any speculation about taken/not taken!

- Late clears: TODO explain the high rate (30-35%) when branch_count >=7 and alignment >=2^12

**Only conditional branches**

- We have very low rates for all abserved parameters which is expected as our conditional branches are 1. a loop with a counter and a forward branch once the loop is finished (with the same condition). So we expect that the _loop branch predictor_ will handle them all except the forward one which would result in a 1/26 misprediction.
    There is some noise prevalent from different background processes which interfere with the ran experiments or the initial state of the BTB being different, despite the best effort to avoid additionnal noise as much as possible. When rerunning the same test, these ouliers are not present anymore. 

## Unconditional branches

**Only unconditional branches**

In this test scenario, we do 5 jumps: An initial one over the span of the wanted alignment (plus a few extra instructions) and then we jump back up a quarter of the space at a time until the last jump back down.

```
jmp %%end
align {align}/4
%%next3:
jmp %%finish
align {align}/4
%%next2:
jmp %%next3
align {align}/4
%%next1:
jmp %%next2
align {align}/4
%%end:
jmp %%next1
%%finish:
```

There are only uncondtional jumps so there should be no noise due to the taken/not taken choices in this test.

- We can observe that for an alignment over 2^14, only the first block of branches (the 5 jumps as explained above) can be processed by the BPU, if we try with more branch blocks, we have an extreme (90-100%) resteer rate! This seems to be due to the fact that our 5 jumps fill the BTB and the following branches result in a resteer.

## Never taken branches

As expected (because not taken branches do not get added to the BTB) adding a never taken branch does not affect the resteers whatsoever.



### Bogus branches

Instructions that end up in the BTB that are not branches and will be evicted as soon as detected. Could not  create such a situation as of now so the doubt about the working condition of the bogus register remains.



## Indirect branches

TODO: some explanantions [here](https://riptutorial.com/x86/example/20468/unconditional-jumps) ?