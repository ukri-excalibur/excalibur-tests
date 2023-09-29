import os
import post_processing as post
import pytest
import shutil
import subprocess as sp

import pandas as pd
from pathlib import Path

# Run given benchmark with reframe using subprocess
def run_benchmark(path):
    sp.run("reframe -c " + path + " -r", shell=True)

# Clean unnecessary files and folders at end of test after running reframe
def benchmark_cleanup(remove_test_logs):

    # remove residual folders
    shutil.rmtree("stage", ignore_errors=True)
    shutil.rmtree("output", ignore_errors=True)
    # remove graph
    if os.path.isfile("Title.html"):
        os.remove("Title.html")

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
    test_name, params = post.get_display_name_info(display_name)

    # check param length, names, and values
    assert test_name == "TestName"
    assert len(params) == 3
    assert (params["param1"] == "one") & (params["param2"] == "two") & (params["param3"] == "three")

    display_name = "TestName"
    _, params = post.get_display_name_info(display_name)

    # no params expected
    assert len(params) == 0

@pytest.fixture(scope="module")
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

    sombrero_log = "SombreroBenchmark.log"
    # look for newly generated log file
    for root, _, files in os.walk(perflog_path):
        if files:
            # if file is found, get file dir path
            if sombrero_log in files:
                # perflog path with <system>/<partition>
                perflog_path = root
    # get log file path
    sombrero_log_path = os.path.join(perflog_path, sombrero_log)

    # create a changed log file
    sombrero_changed_log = "SombreroBenchmarkChanged.log"
    sombrero_changed_log_path = os.path.join(perflog_path, sombrero_changed_log)

    # create an incomplete log file
    sombrero_incomplete_log = "SombreroBenchmarkIncomplete.log"
    sombrero_incomplete_log_path = os.path.join(perflog_path, sombrero_incomplete_log)

    if os.path.exists(sombrero_log_path):
        # copy and modify regular log file
        shutil.copyfile(sombrero_log_path, sombrero_changed_log_path)
        shutil.copyfile(sombrero_log_path, sombrero_incomplete_log_path)

        # add new column to changed log
        changed_df = pd.read_csv(sombrero_changed_log_path, delimiter="|")
        changed_df.insert(0, "id", [i+1 for i in changed_df.index])
        # change one display name
        changed_df.at[1, "display_name"] += " %extra_param=5"
        # change job completion times
        changed_df["job_completion_time"] = ["2000-01-01T12:30:15", "2000-03-01T12:30:15", "2000-09-01T12:30:15", "2000-12-01T12:30:15"]
        changed_df.to_csv(sombrero_changed_log_path, sep="|", index=False)

        # remove required column from incomplete log
        incomplete_df = pd.read_csv(sombrero_incomplete_log_path, delimiter="|")
        incomplete_df.drop("flops_value", axis=1, inplace=True)
        incomplete_df.to_csv(sombrero_incomplete_log_path, sep="|", index=False)

    yield sombrero_log_path, sombrero_changed_log_path, sombrero_incomplete_log_path

    # teardown
    # clean unnecessary files and folders
    benchmark_cleanup(remove_test_logs)

# Test that perflog parsing works and information can be extracted to an appropriate DataFrame
def test_read_perflog(run_sombrero):

    sombrero_log_path, _, sombrero_incomplete_log_path = run_sombrero

    # check the sombrero log path is valid
    assert os.path.exists(sombrero_log_path)
    # if the incomplete log file hasn't been created, something went wrong
    assert os.path.exists(sombrero_incomplete_log_path)

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

    EXPECTED_FIELDS = ["job_completion_time", "version", "info", "jobid", "num_tasks", "num_cpus_per_task", "num_tasks_per_node", "num_gpus_per_node", "flops_value", "flops_unit", "flops_ref", "flops_lower_thres", "flops_upper_thres", "spack_spec", "test_name", "tasks", "cpus_per_task", "system", "partition", "environ", "OMP_NUM_THREADS", "tags"]

    # check example perflog file is read appropriately
    # check all expected columns are present
    assert all(c in EXPECTED_FIELDS for c in df.columns.tolist())
    # check the expected number of rows is present
    assert len(df) == 4
    # check all cells in first row contain something
    assert all(df[column][0] != "" for column in df)
    # check test name matches
    assert df["test_name"][0] == "SombreroBenchmark"
    # check tags match
    assert df["tags"][0] == "example"

# Test that high-level control script works as expected
def test_high_level_script(run_sombrero):

    sombrero_log_path, sombrero_changed_log_path, sombrero_incomplete_log_path = run_sombrero
    post_ = post.PostProcessing()

    # check expected failure from invalid log file
    try:
        post_.run_post_processing(sombrero_incomplete_log_path, {})
    except FileNotFoundError:
        assert True
    else:
        assert False

    # check expected failure from lack of axis information
    try:
        post_.run_post_processing(sombrero_log_path, {})
    except KeyError:
        assert True
    else:
        assert False

    # check expected failure from invalid column
    try:
        post_.run_post_processing(sombrero_log_path, {"series": [], "x_axis": {"value": "fake_column", "units": {"custom": None}}, "y_axis": {"value": "flops_value", "units": {"column": "flops_unit"}}})
    except KeyError:
        assert True
    else:
        assert False

    # check expected failure from invalid filter column
    try:
        post_.run_post_processing(sombrero_log_path, {"filters": [["fake_column", "==", 2]], "series": [], "x_axis": {"value": "tasks", "units": {"custom": None}}, "y_axis": {"value": "flops_value", "units": {"column": "flops_unit"}}})
    except KeyError:
        assert True
    else:
        assert False

    # check expected failure from invalid filter operator
    try:
        post_.run_post_processing(sombrero_log_path, {"filters": [["tasks", "!!", 2]], "series": [], "x_axis": {"value": "tasks", "units": {"custom": None}}, "y_axis": {"value": "flops_value", "units": {"column": "flops_unit"}}})
    except KeyError:
        assert True
    else:
        assert False

    # check expected failure from invalid filter value type
    try:
        post_.run_post_processing(sombrero_log_path, {"filters": [["flops_value", ">", "1"]], "series": [], "x_axis": {"value": "tasks", "units": {"custom": None}}, "y_axis": {"value": "flops_value", "units": {"column": "flops_unit"}}})
    except TypeError:
        assert True
    else:
        assert False

    # check expected failure from filtering out every row
    try:
        post_.run_post_processing(sombrero_log_path, {"filters": [["tasks", ">", 2]], "series": [], "x_axis": {"value": "tasks", "units": {"custom": None}}, "y_axis": {"value": "flops_value", "units": {"column": "flops_unit"}}})
    except pd.errors.EmptyDataError:
        assert True
    else:
        assert False

    # check expected failure from row number vs unique x-axis value number mismatch
    try:
        df = post_.run_post_processing(sombrero_log_path, {"filters": [], "series": [], "x_axis": {"value": "tasks", "units": {"custom": None}}, "y_axis": {"value": "flops_value", "units": {"column": "flops_unit"}}})
    except Exception:
        assert True
    else:
        assert False

    # check correct display name parsing
    try:
        df = post_.run_post_processing(sombrero_changed_log_path, {"filters": [], "series": [], "x_axis": {"value": "tasks", "units": {"custom": None}}, "y_axis": {"value": "cpus_per_task", "units": {"column": "extra_param"}}})
    except Exception as e:
        # three param columns found in changed log
        EXPECTED_FIELDS = ["tasks", "cpus_per_task", "extra_param"]
        # FIXME: assert a certain column dtype for the extra param here?
        assert e.args[1].columns.tolist() == EXPECTED_FIELDS
    else:
        assert False

    # check correct date filtering
    df = post_.run_post_processing(sombrero_changed_log_path, {"title": "Title", "filters": [["job_completion_time", ">", "2000-06-01T12:30:15"]], "series": [], "x_axis": {"value": "job_completion_time", "units": {"custom": None}}, "y_axis": {"value": "flops_value", "units": {"column": "flops_unit"}}})
    # check returned subset is as expected
    assert len(df) == 2

    # check correct concatenation of two dataframes with different columns
    try:
        # get collated dataframe subset
        df = post_.run_post_processing(Path(sombrero_log_path).parent, {"filters": [], "series": [], "x_axis": {"value": "tasks", "units": {"custom": None}}, "y_axis": {"value": "flops_value", "units": {"column": "flops_unit"}}})
    except Exception as e:
        # dataframe has records from both files
        assert len(e.args[1]) == 8
    else:
        assert False

    # get filtered dataframe subset
    df = post_.run_post_processing(sombrero_log_path, {"title": "Title", "filters": [["tasks", ">", 1], ["cpus_per_task", "==", 2]], "series": [], "x_axis": {"value": "tasks", "units": {"custom": None}}, "y_axis": {"value": "flops_value", "units": {"column": "flops_unit"}}})

    EXPECTED_FIELDS = ["tasks", "flops_value", "flops_unit"]
    # check returned subset is as expected
    assert df.columns.tolist() == EXPECTED_FIELDS
    assert len(df) == 1
