import json

import pandas as pd
import typer


def load_stats(path):
    with open(path) as f:
        data = json.load(f)

    commit = data["commit_info"]["id"]

    rows = []
    for d in data["benchmarks"]:
        rows.append({"Benchmark": d["name"], "mean": d["stats"]["mean"]})

    return commit, pd.DataFrame(rows)


def make_report(old_path, new_path, out_file):
    old = load_stats(old_path)
    new = load_stats(new_path)

    # Merge on benchmark name
    df = old[-1].merge(new[-1], on="Benchmark", suffixes=("_old", "_new"))

    df["Percent Change"] = 100 * (df["mean_new"] - df["mean_old"]) / df["mean_old"]
    df["Percent Change"] = df["Percent Change"].map("{:+.2f}".format)

    # Format runtimes
    df["mean_old"] = df["mean_old"].map("{:.5f}".format)
    df["mean_new"] = df["mean_new"].map("{:.5f}".format)

    # Change column names to commit ids
    df = df.rename(
        columns={
            "mean_new": f"Mean (s) HEAD {new[0]}",
            "mean_old": f"Mean (s) BASE {old[0]}",
        }
    )

    df.to_markdown(out_file, index=False)

    # Print report to logs
    print(df.to_markdown(index=False))


if __name__ == "__main__":
    typer.run(make_report)
