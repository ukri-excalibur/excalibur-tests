# OSU Micro-Benchmarks

http://mvapich.cse.ohio-state.edu/static/media/mvapich/README-OMB.txt

The following tests are run (extracted performance variables described in brackets):

On 2x nodes using 1x process per node:
- `osu_bw` - bandwidth (max value over all message sizes)
- `osu_latency` - latency (min value over all message sizes)
- `osu_bibw` - bi-directional bandwidth (max value over all message sizes)

On 2x nodes using as many processes per node as there are physical cores:
- `osu_allgather` - latency (mean value calculated at each message size over pairs, then min taken over all message sizes)
- `osu_allreduce` - as above
- `osu_alltoall` - as above

The following tags are defined:
    - Test name, as given above without the leading "osu_"

# Running

Run all tests using e.g.:

```
reframe -C reframe_config.py -c apps/omb/ --run --performance-report
```

Run only specified benchmark, by choosing the corresponding tag:

```
reframe -C reframe_config.py -c apps/omb/ --run --performance-report --tag alltoall
reframe -C reframe_config.py -c apps/omb/ --run --performance-report --tag bw
```
