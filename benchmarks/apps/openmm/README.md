# OpenMM benchmark

[OpenMM](https://openmm.org/) is high-performance toolkit for molecular simulation.
This directory includes a test based on the 1400k atom benchmark from the [HECBioSim](https://www.hecbiosim.ac.uk/access-hpc/benchmarks) suite.
***Note***: this benchmark can run only on systems with a CUDA GPU.

## Usage

From the top-level directory of the repository, you can run the benchmarks with

```sh
reframe -c benchmarks/apps/openmm -r --performance-report
```

## Figure of merit

The output of the program looks like

```
#"Progress (%)" "Step"  "Potential Energy (kJ/mole)"    "Kinetic Energy (kJ/mole)"      "Total Energy (kJ/mole)"        "Temperature (K)"       "Speed (ns/day)"        "Time Remaining"
10.0%   1000    -15688785.887127012     3656752.4413931114      -12032033.445733901     301.1644297760901       0       --
20.0%   2000    -15722326.52227436      3651648.2543405197      -12070678.26793384      300.7440568884525       8.58    2:41
30.0%   3000    -15748457.618506134     3653282.2518931925      -12095175.366612941     300.8786303793008       8.6     2:20
40.0%   4000    -15766187.389856085     3650127.3583686342      -12116060.03148745      300.6187982674595       8.6     2:00
50.0%   5000    -15771978.47168088      3640930.7606806774      -12131047.711000202     299.86138082043146      8.61    1:40
60.0%   6000    -15779433.041706115     3640669.6428865143      -12138763.398819601     299.8398755660168       8.65    1:19
70.0%   7000    -15774388.543227583     3646512.6161559885      -12127875.927071594     300.3210937346243       8.67    0:59
80.0%   8000    -15777731.520400822     3641287.017230322       -12136444.5031705       299.89072155441534      8.68    0:39
90.0%   9000    -15784781.923775911     3647212.6162459007      -12137569.30753001      300.3787446506489       8.7     0:19
100.0%  10000   -15794411.8787518       3646944.5551444986      -12147467.323607301     300.3566675562755       8.71    0:00
```

The figure of merit is the speed of the last step, in units of `ns/day`.
In this example, the capture figure of merit is `8.71`.
