import os
import shutil
import subprocess as sp
from pathlib import Path

import pandas as pd
import perflog_handler as log_hand
import pytest
from config_handler import ConfigHandler
from perflog_handler import PerflogHandler
from post_processing import PostProcessing


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
    test_name, params = log_hand.get_display_name_info(display_name)

    # check param length, names, and values
    assert test_name == "TestName"
    assert len(params) == 3
    assert (params["param1"] == "one") & (params["param2"] == "two") & (params["param3"] == "three")

    display_name = "TestName"
    _, params = log_hand.get_display_name_info(display_name)

    # no params expected
    assert len(params) == 0


# Test that recursive unpacking of key columns works as expected
def test_key_col_unpacking():

    test_dict1 = {"benchmark": "bench1", "bench1": {"compiler": {"name": "compiler1", "version": 9.2}}}
    test_dict2 = {"benchmark": "bench2", "compiler": {"name": "compiler2", "version": 12.1},
                  "variants": {"cuda": True}, "mpi": ""}

    # flatten test dicts into key columns dicts
    key_cols = [log_hand.find_key_cols(r, key_cols={}) for r in [test_dict1, test_dict2]]

    # expected results
    assert key_cols == [
        {"benchmark": "bench1", "bench1_compiler_name": "compiler1", "bench1_compiler_version": 9.2},
        {"benchmark": "bench2", "compiler_name": "compiler2", "compiler_version": 12.1,
         "variants_cuda": True, "mpi": ""}]


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
    sombrero_bench_path = os.path.join(post_processing_dir.parent /
                                       "benchmarks/examples/sombrero/sombrero.py")

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
        changed_df["job_completion_time"] = ["2000-01-01T12:30:15", "2000-03-01T12:30:15",
                                             "2000-09-01T12:30:15", "2000-12-01T12:30:15"]
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
        log_hand.read_perflog(sombrero_incomplete_log_path)
    except KeyError:
        assert True
    # if an error hasn't been thrown, something went wrong
    else:
        assert False

    # get dataframe from complete perflog
    df = log_hand.read_perflog(sombrero_log_path)

    EXPECTED_FIELDS = ["job_completion_time", "reframe version", "info", "jobid", "num_tasks",
                       "num_cpus_per_task", "num_tasks_per_node", "num_gpus_per_node",
                       "flops_value", "flops_unit", "flops_ref", "flops_lower_thres",
                       "flops_upper_thres", "spack_spec", "test_name", "tasks", "cpus_per_task",
                       "system", "partition", "job_nodelist", "environ", "OMP_NUM_THREADS",
                       "sombrero_compiler_name", "sombrero_compiler_version",
                       "sombrero_variants_build_system", "sombrero_mpi", "tags"]

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

    # check expected failure from nonexistent log file
    try:
        PerflogHandler(os.path.join(Path(sombrero_log_path).parent, "SombreroBenchmarkNonexistent.log"))
    except FileNotFoundError:
        assert True
    else:
        assert False

    # check expected failure from invalid log file
    try:
        PerflogHandler(sombrero_incomplete_log_path)
    except FileNotFoundError:
        assert True
    else:
        assert False

    # check expected failure from lack of config information
    try:
        ConfigHandler({})
    except KeyError:
        assert True
    else:
        assert False

    # check expected failure from invalid (filter) column
    try:
        PostProcessing(sombrero_log_path).run_post_processing(
            ConfigHandler(
                {"title": "Title",
                 "x_axis": {"value": "tasks",
                            "units": {"custom": None}},
                 "y_axis": {"value": "flops_value",
                            "units": {"column": "flops_unit"}},
                 "filters": {"and": [["fake_column", "==", 2]],
                             "or": []},
                 "series": [],
                 "column_types": {"fake_column": "int",
                                  "flops_value": "float",
                                  "flops_unit": "str"},
                 "extra_columns_to_csv": []}))
    except KeyError as e:
        assert e.args[1] == ["fake_column"]
    else:
        assert False

    # check expected failure from invalid filter operator
    try:
        PostProcessing(sombrero_log_path).run_post_processing(
            ConfigHandler(
                {"title": "Title",
                 "x_axis": {"value": "tasks",
                            "units": {"custom": None}},
                 "y_axis": {"value": "flops_value",
                            "units": {"column": "flops_unit"}},
                 "filters": {"and": [["tasks", "!!", 2]],
                             "or": []},
                 "series": [],
                 "column_types": {"tasks": "int",
                                  "flops_value": "float",
                                  "flops_unit": "str"},
                 "extra_columns_to_csv": []}))
    except KeyError as e:
        assert e.args[1] == "!!"
    else:
        assert False

    # check expected failure from invalid filter value type
    try:
        PostProcessing(sombrero_log_path).run_post_processing(
            ConfigHandler(
                {"title": "Title",
                 "x_axis": {"value": "tasks",
                            "units": {"custom": None}},
                 "y_axis": {"value": "flops_value",
                            "units": {"column": "flops_unit"}},
                 "filters": {"and": [["flops_value", ">", "v"]],
                             "or": []},
                 "series": [],
                 "column_types": {"tasks": "int",
                                  "flops_value": "float",
                                  "flops_unit": "str"},
                 "extra_columns_to_csv": []}))
    except ValueError:
        assert True
    else:
        assert False

    # check expected failure from filtering out every row
    try:
        PostProcessing(sombrero_log_path).run_post_processing(
            ConfigHandler(
                {"title": "Title",
                 "x_axis": {"value": "tasks",
                            "units": {"custom": None}},
                 "y_axis": {"value": "flops_value",
                            "units": {"column": "flops_unit"}},
                 "filters": {"and": [["tasks", ">", 2]],
                             "or": []},
                 "series": [],
                 "column_types": {"tasks": "int",
                                  "flops_value": "float",
                                  "flops_unit": "str"},
                 "extra_columns_to_csv": []}))
    except pd.errors.EmptyDataError:
        assert True
    else:
        assert False

    # check expected failure from row number vs unique x-axis value number mismatch
    try:
        df = PostProcessing(sombrero_log_path).run_post_processing(
            ConfigHandler(
                {"title": "Title",
                 "x_axis": {"value": "tasks",
                            "units": {"custom": None}},
                 "y_axis": {"value": "flops_value",
                            "units": {"column": "flops_unit"}},
                 "filters": {"and": [], "or": []},
                 "series": [],
                 "column_types": {"tasks": "int",
                                  "flops_value": "float",
                                  "flops_unit": "str"},
                 "extra_columns_to_csv": []}))
    except RuntimeError:
        assert True
    else:
        assert False

    # check correct display name parsing
    try:
        df = PostProcessing(sombrero_changed_log_path).run_post_processing(
            ConfigHandler(
                {"title": "Title",
                 "x_axis": {"value": "tasks",
                            "units": {"custom": None}},
                 "y_axis": {"value": "cpus_per_task",
                            "units": {"column": "extra_param"}},
                 "filters": {"and": [], "or": []},
                 "series": [],
                 "column_types": {"tasks": "int",
                                  "cpus_per_task": "int",
                                  "extra_param": "int"},
                 "extra_columns_to_csv": []}))
    except RuntimeError as e:
        # three param columns found in changed log
        EXPECTED_FIELDS = ["tasks", "cpus_per_task", "extra_param"]
        assert e.args[1].columns.tolist() == EXPECTED_FIELDS
        assert pd.api.types.is_integer_dtype(e.args[1]["extra_param"].dtype)
    else:
        assert False

    # check correct date filtering
    df = PostProcessing(sombrero_changed_log_path).run_post_processing(
        ConfigHandler(
            {"title": "Title",
             "x_axis": {"value": "job_completion_time",
                        "units": {"custom": None}},
             "y_axis": {"value": "flops_value",
                        "units": {"column": "flops_unit"}},
             "filters": {"and": [["job_completion_time", ">", "2000-06-01T12:30:15"]],
                         "or": []},
             "series": [],
             "column_types": {"job_completion_time": "datetime",
                              "flops_value": "float",
                              "flops_unit": "str"},
             "extra_columns_to_csv": []}))
    # check returned subset is as expected
    assert len(df) == 2

    # check correct or filtering
    df = PostProcessing(sombrero_log_path).run_post_processing(
        ConfigHandler(
            {"title": "Title",
             "x_axis": {"value": "tasks",
                        "units": {"custom": None}},
             "y_axis": {"value": "flops_value",
                        "units": {"column": "flops_unit"}},
             "filters": {"and": [],
                         "or": [["tasks", ">", "1"], ["tasks", "<", "2"]]},
             "series": [["cpus_per_task", "1"], ["cpus_per_task", "2"]],
             "column_types": {"tasks": "int",
                              "cpus_per_task": "int",
                              "flops_value": "float",
                              "flops_unit": "str"},
             "extra_columns_to_csv": []}))
    # check returned subset is as expected
    assert len(df) == 4

    # check correct column scaling
    dfs = PostProcessing(sombrero_log_path).run_post_processing(
        ConfigHandler(
            {"title": "Title",
             "x_axis": {"value": "tasks",
                        "units": {"custom": None}},
             "y_axis": {"value": "flops_value",
                        "units": {"column": "flops_unit"},
                        "scaling": {"column": {"name": "OMP_NUM_THREADS"}}},
             "filters": {"and": [["cpus_per_task", "==", 2]],
                         "or": []},
             "series": [],
             "column_types": {"tasks": "int",
                              "flops_value": "float",
                              "flops_unit": "str",
                              "cpus_per_task": "int",
                              "OMP_NUM_THREADS": "int"},
             "extra_columns_to_csv": []}))
    # check flops values are halved compared to previous df
    assert (dfs["flops_value"].values == df[df["cpus_per_task"] == 2]["flops_value"].values/2).all()

    # check correct column + series scaling
    dfs = PostProcessing(sombrero_log_path).run_post_processing(
        ConfigHandler(
            {"title": "Title",
             "x_axis": {"value": "tasks",
                        "units": {"custom": None}},
             "y_axis": {"value": "flops_value",
                        "units": {"column": "flops_unit"},
                        "scaling": {"column": {"name": "flops_value",
                                               "series": 0}}},
             "filters": {"and": [], "or": []},
             "series": [["cpus_per_task", 1], ["cpus_per_task", 2]],
             "column_types": {"tasks": "int",
                              "flops_value": "float",
                              "flops_unit": "str",
                              "cpus_per_task": "int"},
             "extra_columns_to_csv": []}))
    assert (dfs[dfs["cpus_per_task"] == 1]["flops_value"].values ==
            df[df["cpus_per_task"] == 1]["flops_value"].values /
            df[df["cpus_per_task"] == 1]["flops_value"].values).all()
    assert (dfs[dfs["cpus_per_task"] == 2]["flops_value"].values ==
            df[df["cpus_per_task"] == 2]["flops_value"].values /
            df[df["cpus_per_task"] == 1]["flops_value"].values).all()

    # check correct column + series + x value scaling
    dfs = PostProcessing(sombrero_log_path).run_post_processing(
        ConfigHandler(
            {"title": "Title",
             "x_axis": {"value": "tasks",
                        "units": {"custom": None}},
             "y_axis": {"value": "flops_value",
                        "units": {"column": "flops_unit"},
                        "scaling": {"column": {"name": "flops_value",
                                               "series": 0,
                                               "x_value": 2}}},
             "filters": {"and": [], "or": []},
             "series": [["cpus_per_task", 1], ["cpus_per_task", 2]],
             "column_types": {"tasks": "int",
                              "flops_value": "float",
                              "flops_unit": "str",
                              "cpus_per_task": "int"},
             "extra_columns_to_csv": []}))
    assert (dfs["flops_value"].values == df["flops_value"].values /
            df[(df["cpus_per_task"] == 1) & (df["tasks"] == 2)]["flops_value"].iloc[0]).all()

    # check correct custom scaling
    dfs = PostProcessing(sombrero_log_path).run_post_processing(
        ConfigHandler(
            {"title": "Title",
             "x_axis": {"value": "tasks",
                        "units": {"custom": None}},
             "y_axis": {"value": "flops_value",
                        "units": {"column": "flops_unit"},
                        "scaling": {"custom": 2}},
             "filters": {"and": [["cpus_per_task", "==", 2]],
                         "or": []},
             "series": [],
             "column_types": {"tasks": "int",
                              "flops_value": "float",
                              "flops_unit": "str",
                              "cpus_per_task": "int"},
             "extra_columns_to_csv": []}))
    # check flops values are halved compared to previous df
    assert (dfs["flops_value"].values == df[df["cpus_per_task"] == 2]["flops_value"].values/2).all()

    # check expected failure from scaling by incorrect column type
    try:
        df = PostProcessing(sombrero_log_path).run_post_processing(
            ConfigHandler(
                {"title": "Title",
                 "x_axis": {"value": "tasks",
                            "units": {"custom": None}},
                 "y_axis": {"value": "flops_value",
                            "units": {"column": "flops_unit"},
                            "scaling": {"column": {"name": "OMP_NUM_THREADS"}}},
                 "filters": {"and": [], "or": []},
                 "series": [["cpus_per_task", 1], ["cpus_per_task", 2]],
                 "column_types": {"tasks": "int",
                                  "flops_value": "float",
                                  "flops_unit": "str",
                                  "cpus_per_task": "int",
                                  "OMP_NUM_THREADS": "str"},
                 "extra_columns_to_csv": []}))
    except TypeError:
        assert True

    # check expected failure from scaling by incompatible custom type
    try:
        df = PostProcessing(sombrero_log_path).run_post_processing(
            ConfigHandler(
                {"title": "Title",
                 "x_axis": {"value": "tasks",
                            "units": {"custom": None}},
                 "y_axis": {"value": "flops_value",
                            "units": {"column": "flops_unit"},
                            "scaling": {"custom": "s"}},
                 "filters": {"and": [["cpus_per_task", "==", 2]],
                             "or": []},
                 "series": [],
                 "column_types": {"tasks": "int",
                                  "flops_value": "float",
                                  "flops_unit": "str",
                                  "cpus_per_task": "int"},
                 "extra_columns_to_csv": []}))
    except ValueError:
        assert True

    # check correct concatenation of two dataframes with different columns
    try:
        # get collated dataframe subset
        df = PostProcessing(Path(sombrero_log_path).parent).run_post_processing(
            ConfigHandler(
                {"title": "Title",
                 "x_axis": {"value": "tasks",
                            "units": {"custom": None}},
                 "y_axis": {"value": "flops_value",
                            "units": {"column": "flops_unit"}},
                 "filters": {"and": [], "or": []},
                 "series": [],
                 "column_types": {"tasks": "int",
                                  "flops_value": "float",
                                  "flops_unit": "str"},
                 "extra_columns_to_csv": []}))
    except RuntimeError as e:
        # dataframe has records from both files
        assert len(e.args[1]) == 8
    else:
        assert False

    # get filtered dataframe subset
    df = PostProcessing(sombrero_log_path).run_post_processing(
        ConfigHandler(
            {"title": "Title",
             "x_axis": {"value": "tasks",
                        "units": {"custom": None}},
             "y_axis": {"value": "flops_value",
                        "units": {"column": "flops_unit"}},
             "filters": {"and": [["tasks", ">", 1], ["cpus_per_task", "==", 2]],
                         "or": []},
             "series": [],
             "column_types": {"tasks": "int",
                              "flops_value": "float",
                              "flops_unit": "str",
                              "cpus_per_task": "int"},
             "extra_columns_to_csv": []}))

    EXPECTED_FIELDS = ["tasks", "flops_value", "flops_unit"]
    # check returned subset is as expected
    assert df.columns.tolist() == EXPECTED_FIELDS
    assert len(df) == 1

    # get filtered dataframe with extra columns for csv
    df = PostProcessing(sombrero_log_path, save=True).run_post_processing(
        ConfigHandler(
            {"title": "Title",
             "x_axis": {"value": "tasks",
                        "units": {"custom": None}},
             "y_axis": {"value": "flops_value",
                        "units": {"column": "flops_unit"}},
             "filters": {"and": [["tasks", ">", 1], ["cpus_per_task", "==", 2]],
                         "or": []},
             "series": [],
             "column_types": {"tasks": "int",
                              "flops_value": "float",
                              "flops_unit": "str",
                              "cpus_per_task": "int"},
             "extra_columns_to_csv": ["spack_spec"]}
        ))

    EXPECTED_FIELDS = ["tasks", "flops_value", "flops_unit"]
    # check returned subset is as expected
    assert df.columns.tolist() == EXPECTED_FIELDS
    assert len(df) == 1

    EXPECTED_FIELDS.append("spack_spec")
    # check subset written to csv is as expected
    output_file = "output.csv"
    df_saved = pd.read_csv(output_file, index_col=0)
    assert df_saved.columns.tolist() == EXPECTED_FIELDS
    assert len(df_saved) == 1

    # get filtered dataframe with duplicated extra columns for csv
    df = PostProcessing(sombrero_log_path, save=True).run_post_processing(
        ConfigHandler(
            {"title": "Title",
             "x_axis": {"value": "tasks",
                        "units": {"custom": None}},
             "y_axis": {"value": "flops_value",
                        "units": {"column": "flops_unit"}},
             "filters": {"and": [["tasks", ">", 1], ["cpus_per_task", "==", 2]],
                         "or": []},
             "series": [],
             "column_types": {"tasks": "int",
                              "flops_value": "float",
                              "flops_unit": "str",
                              "cpus_per_task": "int"},
             "extra_columns_to_csv": ["tasks", "tasks"]}
        ))

    EXPECTED_FIELDS = ["tasks", "flops_value", "flops_unit"]
    # check returned subset is as expected
    assert df.columns.tolist() == EXPECTED_FIELDS
    assert len(df) == 1

    # check subset written to csv is as expected
    output_file = "output.csv"
    df_saved = pd.read_csv(output_file, index_col=0)
    assert df_saved.columns.tolist() == EXPECTED_FIELDS
    assert len(df_saved) == 1
