"""
Compare results from the master model xslx results 

Aggregates averages for correctness, readability, checklist, and detection metrics
Runs group-level statistics (mean, std)
Makes comparative plots across models
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import argparse


def load_model_results(path, model_name):
    df = pd.read_excel(path)
    df["Model"] = model_name
    return df


def encode_fixes_missing(val):
    if isinstance(val, str):
        val = val.strip().lower()
        if val == "infers":
            return 1
        elif val == "nothing":
            return 0
    return np.nan


def compare_llms(file_paths, model_names, output_summary="llm_comparison_summary.xlsx"):

    dfs = [load_model_results(p, name) for p, name in zip(file_paths, model_names)]
    df_all = pd.concat(dfs, ignore_index=True)


    df_all["Fixes_Missing_Num"] = df_all["Fixes_Missing"].apply(encode_fixes_missing)


    for col in ["Correctness", "Flesch_Reading_Ease", "Flesch_Kincaid_Grade",
                "Gunning_Fog_Index", "Type_Token_Ratio", "Checklist_Score",
                "Detects_error", "Fixes_error", "Detects_Missing", "Fixes_Missing_Num"]:
        if col in df_all.columns:
            df_all[col] = pd.to_numeric(df_all[col], errors="coerce")





    metrics = ["Correctness", "Checklist_Score",
               "Detects_error", "Fixes_error", "Detects_Missing", "Fixes_Missing_Num",
               "Flesch_Reading_Ease", "Flesch_Kincaid_Grade", "Gunning_Fog_Index", "Type_Token_Ratio"]

    summary = df_all.groupby("Model")[metrics].agg(["mean", "std"]).round(3)
    summary.columns = ['_'.join(col) for col in summary.columns]
    summary.reset_index(inplace=True)


    summary.to_excel(output_summary, index=False)
    print(f"summary saved to {output_summary}") #Final checker


    plt.figure(figsize=(8, 5))
    melted = df_all.melt(id_vars="Model", value_vars=["Correctness", "Checklist_Score"],
                         var_name="Metric", value_name="Score")
    sns.barplot(data=melted, x="Metric", y="Score", hue="Model", ci="sd")
    plt.title("Model Comparison: Correctness & Conceptual Quality")
    plt.ylabel("Average Score")
    plt.legend(title="Model")
    plt.tight_layout()
    plt.savefig("comparison_correctness_checklist.png", dpi=300)
    plt.show()

 
    plt.figure(figsize=(8, 5))
    detect_cols = ["Detects_error", "Fixes_error", "Detects_Missing"]
    melted2 = df_all.melt(id_vars="Model", value_vars=detect_cols,
                          var_name="Metric", value_name="Rate")
    sns.barplot(data=melted2, x="Metric", y="Rate", hue="Model", ci="sd")
    plt.title("Model Comparison: Error & Missing Data Handling")
    plt.ylabel("Proportion (0–1)")
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig("comparison_error_handling.png", dpi=300)
    plt.show()


    plt.figure(figsize=(8, 5))
    read_cols = ["Flesch_Reading_Ease", "Flesch_Kincaid_Grade", "Gunning_Fog_Index"]
    melted3 = df_all.melt(id_vars="Model", value_vars=read_cols,
                          var_name="Metric", value_name="Score")
    sns.barplot(data=melted3, x="Metric", y="Score", hue="Model", ci="sd")
    plt.title("Model Comparison: Readability Metrics")
    plt.ylabel("Average Score")
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig("comparison_readability.png", dpi=300)
    plt.show()

    return df_all, summary



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare multiple LLMs on evaluation metrics")
    parser.add_argument("--files", nargs=3, required=True)
    parser.add_argument("--models", nargs=3, required=True)
    parser.add_argument("--output", default="llm_comparison_summary.xlsx")
    args = parser.parse_args()
    compare_llms(args.files, args.models, args.output)
