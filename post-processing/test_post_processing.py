import fileinput
import os
from pathlib import Path
import post_processing as post
import re
import shutil
import subprocess as sp

# Run given benchmark with reframe using subprocess
def run_benchmark(path):
    sp.run("reframe -c " + path + " -r", shell=True)

# Clean unnecessary files and folders at end of test after running reframe
def benchmark_cleanup(benchmark_run, remove_test_logs):

    # remove residual folders if test benchmark has been run
    if benchmark_run:
        shutil.rmtree("stage", ignore_errors=True)
        shutil.rmtree("output", ignore_errors=True)

    # remove test log files
    if remove_test_logs:
        shutil.rmtree("perflogs", ignore_errors=True)

# Remove given field from perflog line
def remove_field_from_perflog(line, field_index):

    # parse line
    columns = line.strip().split("|")
    # remove given field
    columns.pop(field_index)
    # convert back to string
    line = "|".join(columns)

    return line

def test_display_name_parsing():

    display_name = "TestName %param1=one %param2=two %param3=three"
    params = post.get_params_from_name(display_name)

    # check param length, names, and values
    assert len(params) == 3
    assert (params["param1"] == "one") & (params["param2"] == "two") & (params["param3"] == "three")

def test_read_perflog():

    REQUIRED_FIELD = "flops_value"
    EXPECTED_FIELDS = ["job_completion_time", "version", "info", "jobid", "num_tasks", "num_cpus_per_task", "num_tasks_per_node", "num_gpus_per_node", "flops_value", "flops_unit", "flops_ref", "flops_lower_thres", "flops_upper_thres", "spack_spec", "display_name", "system", "partition", "environ", "extra_resources", "env_vars", "tags"]

    # set True to remove test log files at the end of the test
    remove_test_logs = True
    # keeps track of whether the test benchmark has been run during this test
    benchmark_run = False

    # absolute path to post-processing directory
    post_processing_dir = Path(__file__).parent
    # change current working dir to avoid
    # potentially deleting non-test perflogs later
    os.chdir(post_processing_dir)
    # resolve relative path from post-processing directory to access sombrero benchmark
    sombrero_bench_path = str((post_processing_dir / "../benchmarks/examples/sombrero/sombrero.py").resolve())

    # get test log file paths
    perflog_path = os.path.join(os.getcwd(),"perflogs/default/default/")
    sombrero_incomplete_log = "SombreroBenchmarkIncomplete.log"
    sombrero_incomplete_log_path = os.path.join(perflog_path, sombrero_incomplete_log)

    # look for existing log files
    sombrero_logs = []
    sombrero_log_re = re.compile(r"^SombreroBenchmark\_\w{8}\.log$")
    for subdirs, dirs, files in os.walk(perflog_path):
        sombrero_logs = list(filter(sombrero_log_re.match, files))

    try:
        # to save time don't re-generate test log files if they already exist
        if not sombrero_logs:
            # use sombrero example to generate new test perflog file
            run_benchmark(sombrero_bench_path)
            benchmark_run = True
            # look for log files again
            for subdirs, dirs, files in os.walk(perflog_path):
                sombrero_logs = list(filter(sombrero_log_re.match, files))
        # check that the log files exist
        if sombrero_logs:
            # arbitrarily pick one of the log file names
            sombrero_log_path = os.path.join(perflog_path, sombrero_logs[0])
        # if the log files haven't been created, something went wrong
        else:
            assert False

        # as above, only re-generate log file if it doesn't exist
        if not os.path.exists(sombrero_incomplete_log_path):
            # copy and modify regular log file
            shutil.copyfile(sombrero_log_path, sombrero_incomplete_log_path)
            required_field_index = 0
            for line in fileinput.input(sombrero_incomplete_log_path, inplace=True):
                # find index of column to be removed
                if fileinput.isfirstline():
                    LOG_FIELDS = line.strip().split("|")
                    required_field_index = LOG_FIELDS.index(REQUIRED_FIELD)
                # remove a required field
                new_line = remove_field_from_perflog(line, required_field_index)
                # inline replacement
                print(new_line, end="\n")
        # if the log file hasn't been created, something went wrong
        if not os.path.exists(sombrero_incomplete_log_path):
            assert False

        # check incomplete log is missing required fields
        try:
            post.read_perflog(sombrero_incomplete_log_path)
        except KeyError:
            assert True
        # if an error hasn't been thrown, something went wrong
        else:
            assert False

        # get dataframe from complete perflog
        df = post.read_perflog(sombrero_log_path)

    finally:
        # clean unnecessary files and folders
        benchmark_cleanup(benchmark_run, remove_test_logs)

    # check example perflog file is read appropriately
    assert df.columns.tolist() == EXPECTED_FIELDS
    # check display name matches
    assert re.compile(r"SombreroBenchmark %tasks=\d %cpus_per_task=\d").match(df["display_name"][0])
    # check tags match
    tag_matches = [len(list(filter(re.compile(rexpr).match, df["tags"][0].split(",")))) > 0 for rexpr in ["example", r"test\d"]]
    assert not (False in tag_matches)
