## Modifications from the original code

None, except the ones to improve the rendering of the matplotlib graphs.
I recreated the same color scheme that Godbolt used on his [website](https://xania.org/201602/haswell-and-ivy-btb) in order to facilitate the comparing of my own results and his.



## Results

I recovered Godbolt's results (about Arrendale, Haswell and ivyBridge) from his website and merged them into a pdf each so that they can easily be compared to ours. They can be found in the `results/Godbolt` folder.

I did several runs of both tests to make sure that the results do not vary from one run to the next. The last run was done with Ubuntu in text only mode in order to reduce the amount of things the computer does in the background to reduce the impact on the tests.

The `2019_09_30_10_00_results_text_only.pdf` and `results.pdf` are the same except that I removed the data about the `branch.py` test because it does not run stable enough (it fails ~40% of time) because the measured timings are varying to much (above the 15% threshold defined by Godbolt).

This test will be removed from future versions of the toolkit because it is only trying to determine if there is a naive implementation of the predictor and [Godbolt found that except for Arrendale](https://xania.org/201602/bpu-part-two), it was not the case and as we are working with more recent CPU generations, there is no useful information to recover from this test.

Other than that, the results from Broadwell are pretty close to the ones of the Haswell generation with a few minor changes in the exact number of redirects but the implementation seems to be very similar. We should therefore be able to continue with Gobolt's assumptions about the Haswell CPUs for our work.