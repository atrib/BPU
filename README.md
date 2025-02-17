# Reverse-Engineering the branch predictor algorithms in modern CPUs

The tools in the repo are based on [Matt Gobolt's tools](https://github.com/mattgodbolt/agner) at commit `3731a0a`.



## Setup

**This was setup on Ubuntu 18.04, for another environment, adapt the commands**

Install required package (`matplotlib`) on the root python install as the script needs to be run as sudo

```bash
sudo su
pip install matplotlib
exit
```

Install the required general-purpose x86 assembler `nasm` 

```bash
sudo apt install nasm
```

If the Gobolt's original code is used, the following line in the  `/src/driver/install.sh` file needs to be modified as follows:  from`insmod -f MSRdrv.ko` to `insmod MSRdrv.ko` . The syntax for the `insmod` command seems to have changed since his work on the project.

The command following command is required to be launched **after each reboot** as it injects the driver in order to be able to read the specific intel registers (ahead not taken, redirects, etc..) in user mode.

```bash
sudo ./agner install
```

It should be compiling the various files as needed be should it not be working as intended, there are two compilations that need to be done, inside the `src`  and  `src/driver` folders. (After a kernel update, it is required to run a `sudo clean` and recompile the driver)

```bash
cd src/
sudo make
cd driver/
# sudo make clean
sudo make
```

___

In order to have more readable graphs, you will need the copy the matplotlib configuration file situated in the `config` folder. The default location where to put the file for matplotlib to recognize it is `~/.config/matplotlib/stylelib/custom.mplstyle `



## Launching the tool

The following commands allow to run the various tests and plot the output:

```bash
# Inject the driver into the kernel (needs ot be done once and after a reboot)
sudo ./agner install

# Run all the tests (by default the outputs are stored in the results.json file)
sudo ./agner test_only

# Plot the results to a pdf file
sudo ./agner plot --pdf output_file.pdf

# Help command
sudo ./agner -h

# Remove the driver after running the tests
sudo ./agner uninstall
```



Output of the help command for quick access if needed:

```
usage: agner [-h] [-r FILE] [--xsize INCHES] [--ysize INCHES] [--dpi DPI]
             [--alternative] [--pdf PDF] [--png template]
             {plot,run,list,test_only,install,uninstall} [TEST [TEST ...]]

Test various microarchitecture parameters

positional arguments:
  {plot,run,list,test_only,install,uninstall}
  TEST                  run test TEST

optional arguments:
  -h, --help            show this help message and exit
  -r FILE, --results-file FILE
                        read or write results to FILE
  --xsize INCHES        set plot X size in inches
  --ysize INCHES        set plot Y size in inches
  --dpi DPI             set plot DPI
  --alternative         output alternative graph
  --pdf PDF             output plot as PDF
  --png template        output plots as template formatted with {test}
                        {subtest}
```



## Different steps

Each step of the project can be found in its own sub-folder with a short readme file describing the changes to the implementation and results.

The full toolkit is copied each time (as its file-size is small) in order to facilitate rerunning experiments without having to jump between commits.



Objectives of each step:

### Step00

- Get [Matt Godbolt's tools](https://github.com/mattgodbolt/agner) to work on my own laptop (Broadwell: i7-5600U)

- Compare results with his and see if they are similar and what is expected

  

### Step01

- Add Branch alignment to 2^0 to the `btb_size` tests

- Figure out if XOR-like function is used for indexing in Broadwell. [Documentation](https://www.usenix.org/conference/usenixsecurity18/presentation/gras)

- If aliasing is possible, try to figure out replacement policy (with series of basic jumps J0, J1, J2, J3, J1, etc and see which ones gets evicted):

  - Least frequently used?
  - Other policy?

- Building eviction sets (with various jumps until the buffer is full and we start seeing evictions). [Documentation](https://arxiv.org/abs/1810.01497)

- Expand on Gobolt's tests and push the analysis further

  

### Step02

**Additional Performance registers**

Check and try to use additional performance registers from Intel (see [documentation](http://www.intel.com/content/dam/www/public/us/en/documents/manuals/64-ia-32-architectures-software-developer-vol-3b-part-2-manual.pdf)) to see if they could be useful in our reverse-engineering effort.

Write some small test cases where we would expect a specific behavior to make sure that the counters do work and are readable correctly and not that we receive a 0 no matter what.

**Reset BTB**

Write some code that shuffles, floods or resets the BTB so that at each run, we have a pseudo-random content in the BTB. We should at least be able to avoid having our previous branches cached.

Alternatively, one could reboot his system as the power loss will result in an empty cache but it is inconvenient and time consuming as the driver needs to be reloaded each time.

**Retro-compatibility**

Added the performance register `BrMispredict` to the step01 code



### Step03

Write several benchmarks and/or test scenarios with the following elements and try to get a better understanding of how the algorithm works:

- only conditional branches
- only unconditional branches
- dummy branches that will never be taken (they should not appear in the BTB)
- bogus branches and their effect: elements in the BTB that are not branches
- forward branches (covered in the only unconditional branches)
- backward branches -> loops
- Indirect branches (not on address but on register value)

See [Vladimir Uzelac's Master thesis](http://www.ece.uah.edu/~milenka/docs/VladimirUzelac.thesis.pdf) for some useful insight (older architecture but the approach should be helpful)

Try more precise tests with new performance registers!



### Step04

Run various test on a Skylake CPU (i7-6700k) and see if the results are similar to the Broadwell ones or if they differ and try to explain why.
