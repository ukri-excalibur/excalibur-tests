import fileinput
import os
from pathlib import Path
import post_processing as post
import pytest
import re
import shutil
import subprocess as sp

# Run given benchmark with reframe using subprocess
def run_benchmark(path):
    sp.run("reframe -c " + path + " -r", shell=True)

# Clean unnecessary files and folders at end of test after running reframe
def benchmark_cleanup(remove_test_logs):

    # remove residual folders
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

# Test that display name parsing works and parameters can be extracted
def test_display_name_parsing():

    display_name = "TestName %param1=one %param2=two %param3=three"
    params = post.get_display_name_params(display_name)

    # check param length, names, and values
    assert len(params) == 3
    assert (params["param1"] == "one") & (params["param2"] == "two") & (params["param3"] == "three")

    display_name = "TestName"
    params = post.get_display_name_params(display_name)

    # no params expected
    assert len(params) == 0

@pytest.fixture()
# Fixture to run sombrero benchmark example, generate perflogs, and clean up after test
def run_sombrero():

    # settings
    # set True to remove test log files at the end of the test
    remove_test_logs = True

    # setup
    # absolute path to post-processing directory
    post_processing_dir = Path(__file__).parent
    # change current working dir to avoid potentially deleting non-test perflogs
    os.chdir(post_processing_dir)
    # remove the test perflog directory if it currently exists
    if os.path.exists("perflogs"):
        shutil.rmtree("perflogs", ignore_errors=True)
    # get test log location path
    perflog_path = os.path.join(post_processing_dir, "perflogs")
    # resolve relative path from post-processing directory to access sombrero benchmark
    sombrero_bench_path = os.path.join(post_processing_dir.parent / "benchmarks/examples/sombrero/sombrero.py")

    # use sombrero example to generate new test perflog file
    run_benchmark(sombrero_bench_path)

    sombrero_logs = []
    sombrero_log_re = re.compile(r"^SombreroBenchmark\_\w{8}\.log$")
    # look for newly generated log files
    for root, dirs, files in os.walk(perflog_path):
        sombrero_logs = list(filter(sombrero_log_re.match, files))
        # if files are found, get file dir path
        if sombrero_logs:
            # perflog path with <system>/<partition>
            perflog_path = root

    sombrero_log_path = ""
    # check the log files exist
    if sombrero_logs:
        # arbitrarily pick one of the log file names
        sombrero_log_path = os.path.join(perflog_path, sombrero_logs[0])

    # create an incomplete log file
    sombrero_incomplete_log = "SombreroBenchmarkIncomplete.log"
    sombrero_incomplete_log_path = os.path.join(perflog_path, sombrero_incomplete_log)

    if os.path.exists(sombrero_log_path):
        # copy and modify regular log file
        shutil.copyfile(sombrero_log_path, sombrero_incomplete_log_path)

        REQUIRED_FIELD = "flops_value"
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

    yield sombrero_logs, sombrero_log_path, sombrero_incomplete_log_path

    # teardown
    # clean unnecessary files and folders
    benchmark_cleanup(remove_test_logs)

# Test that perflog parsing works and information can be extracted to an appropriate DataFrame
def test_read_perflog(run_sombrero):

    sombrero_logs, sombrero_log_path, sombrero_incomplete_log_path = run_sombrero

    # check the log files exist
    if sombrero_logs:
        # check the sombrero log path is valid
        assert os.path.exists(sombrero_log_path)
        # check the expected number of log files has been generated
        assert len(sombrero_logs) ==  4
    # if the log files haven't been created, something went wrong
    else:
        assert False

    # if the incomplete log file hasn't been created, something went wrong
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

    EXPECTED_FIELDS = ["job_completion_time", "version", "info", "jobid", "num_tasks", "num_cpus_per_task", "num_tasks_per_node", "num_gpus_per_node", "flops_value", "flops_unit", "flops_ref", "flops_lower_thres", "flops_upper_thres", "spack_spec", "test_name", "tasks", "cpus_per_task", "system", "partition", "environ", "extra_resources", "env_vars", "tags"]

    # check example perflog file is read appropriately
    # check all expected columns are present
    assert df.columns.tolist() == EXPECTED_FIELDS
    # check all cells in first row contain something
    assert all(df[column][0] != "" for column in df)
    # check test name matches
    assert df["test_name"][0] == "SombreroBenchmark"
    # check tags match
    assert df["tags"][0] == "example"
