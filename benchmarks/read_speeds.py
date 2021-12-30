import json
import math
import time

import bmp_file_reader as bmpr


def read_file_row_by_row(filepath):
    with open(filepath, "r") as file_handle:
        reader = bmpr.BMPFileReader(file_handle)

        for row_i in range(0, reader.get_height()):
            row = reader.get_row(row_i)


def run_benchmark(name, function, arguments, num_times):
    durations = []
    for _ in range(0, num_times):
        before = time.ticks_ms()
        function(*arguments)
        after = time.ticks_ms()

        duration_ms = time.ticks_diff(after, before)

        durations.append(duration_ms)

    return durations


def summarize_results(benchmark_results):
    mean_ms = sum(benchmark_results) / len(benchmark_results)
    stddev_ms = math.sqrt(
        (sum(((x - mean_ms) ** 2 for x in benchmark_results))) / len(benchmark_results)
    )

    mean = f"{mean_ms}ms"
    stddev = f"{stddev_ms}ms"

    return {"mean": mean, "stddev": stddev}


def print_summary(summary):
    print(f'{summary["mean"]} +/- {summary["stddev"]}')


def run_benchmarks(output_stream):
    benchmarks = [
        ("read_file_row_by_row_01", read_file_row_by_row, ("32x32.bmp",), 10),
        ("read_file_row_by_row_02", read_file_row_by_row, ("160x128.bmp",), 10),
    ]

    results = {}
    for b in benchmarks:
        print(b[0], "... ", end="")

        b_results = run_benchmark(b[0], b[1], b[2], b[3])
        summary = summarize_results(b_results)

        print_summary(summary)

        results[b[0]] = summary

    # print(results)

    # TODO: write as csv instead
    json.dump(results, output_stream)


if __name__ == "__main__":
    print("Starting benchmarks...")
    with open("benchmark_results.json", "w") as output_stream:
        run_benchmarks(output_stream)
        print()
