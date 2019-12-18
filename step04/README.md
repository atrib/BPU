## Expand to Skylake processors

Added performance register mapping for Skylake processors to agner's tools -> needed to update the CPP agner files which had been refactored in the mean time as Godbolt used the ones from 2016 which did not include compatibility with Skylake registers at the time.

Took some time to make it work but it is fine now.

## Rerun of previous test in order to compare

- **capacity_test:** Similar results overall but an alignment of 2^0 and 2^1 result in a 50% resteers on the Skylake processor (0% resteers on Broadwell). Still 4096 branches that can be fit into the BTB without resteers. On the Skylake CPU the transition for a 2^5 alignment and over is more abrupt than on Broadwell.
- **nb_ways:** We have the same fitting behavior but the misrate for 6 branches (and alignment >= 2^12) is higher: ~27% vs 16% beforehand which hints at a different replacement policy for the BTB.
- **nb_ways2:** Same as for the nb_ways test, with only the misprediction rate that changer
- **nb_ways3:** The Skylake processor can fit more branches if the branch alignment is 2^13
- **set_collision:** The overall resteer rates follow a similar pattern but we have an offset on the alignment: the 2^12 value on Broadwell can be found at 2^13 on Skylake
- **new registers:** The 7 new registers that work on Broadwell do as well on Skylake so we will be able to run the same tests on both and will be able to monitor them with the same performance registers.
- **loop tests:** The results are very similar for both the conditional and unconditional branches, we can expect that the loop predictor is unchanged between the two processor generations.