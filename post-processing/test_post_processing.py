import fileinput
import os
from pathlib import Path
import post_processing as post
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
def remove_field_from_perflog(line, field):

    # parse line
    columns = line.strip().split("|")
    LOG_FIELDS = [c.split("=")[0] for c in columns]
    # convert to dictionary for easy manipulation
    record = dict(zip(LOG_FIELDS, (c.split("=")[-1] for c in columns)))

    # remove given field
    record.pop(field)
    # convert back to string
    line = "|".join(["=".join([key, value]) for key, value in record.items()])

    return line

def test_display_name_parsing():

    display_name = "TestName %param1=one %param2=two %param3=three"
    params = post.get_params_from_name(display_name)

    # check param length, names, and values
    assert len(params) == 3
    assert (params["param1"] == "one") & (params["param2"] == "two") & (params["param3"] == "three")

def test_read_perflog():

    REQUIRED_FIELD = "completion_time"
    EXPECTED_FIELDS = ["completion_time", "reframe", "jobid", "perf_var", "perf_val", "units", "num_tasks", "num_cpus_per_task", "num_tasks_per_node", "ref", "lower", "upper", "spack_spec", "display_name", "system", "partition", "environ", "env_vars", "variables", "tags"]

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

    # resolve test log file paths
    sombrero_log = "SombreroBenchmark.log"
    sombrero_imcomplete_log = "SombreroBenchmarkIncomplete.log"
    perflog_path = os.path.join(os.getcwd(),"perflogs/generic/default/")
    sombrero_log_path = os.path.join(perflog_path, sombrero_log)
    sombrero_incomplete_log_path = os.path.join(perflog_path, sombrero_imcomplete_log)

    try:
        # to save time don't re-generate test log file if it already exists
        if not os.path.exists(sombrero_log_path):
            # use sombrero example to generate new test perflog file
            run_benchmark(sombrero_bench_path)
            benchmark_run = True
            # if the log file hasn't been created, something went wrong
            if not os.path.exists(sombrero_log_path):
                assert False

        # as above, only re-generate log file if it doesn't exist
        if not os.path.exists(sombrero_incomplete_log_path):
            # copy and modify regular log file
            shutil.copyfile(sombrero_log_path, sombrero_incomplete_log_path)
            for line in fileinput.input(sombrero_incomplete_log_path, inplace=True):
                # remove a required field
                new_line = remove_field_from_perflog(line, REQUIRED_FIELD)
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
    assert df["display_name"][0] == "SombreroBenchmark"
    assert df["tags"][0] == ""
