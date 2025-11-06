"""
Readability tests but individually based on grade category
 - Flesch–Kincaid Grade Level
 - Flesch Reading Ease
 - Gunning Fog Index
 - Type–Token Ratio


Requires: pandas, textstat, matplotlib, seaborn, openpyxl
"""

import pandas as pd
import textstat
import re
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns








def type_token_ratio(text):
    tokens = re.findall(r'\b\w+\b', str(text).lower())
    if len(tokens) == 0:
        return 0
    return round(len(set(tokens)) / len(tokens), 3)




def analyze_llm_responses(excel_path, model_name):
    df = pd.read_excel(excel_path)


    df["Grade_Level"] = df["Grade_Level"].astype(str).str.strip().str.lower()
    readability_levels = {"5", "8", "10", "university"}


    for col in ["Flesch_Reading_Ease", "Flesch_Kincaid_Grade", "Gunning_Fog_Index", "Type_Token_Ratio"]:
        df[col] = None

    # Compute metrics
    for idx, row in df.iterrows():
        grade = row["Grade_Level"]
        text = str(row.get("Model_Response", ""))

        if grade in readability_levels:
            df.at[idx, "Flesch_Reading_Ease"] = textstat.flesch_reading_ease(text)
            df.at[idx, "Flesch_Kincaid_Grade"] = textstat.flesch_kincaid_grade(text)
            df.at[idx, "Gunning_Fog_Index"] = textstat.gunning_fog(text)
            df.at[idx, "Type_Token_Ratio"] = type_token_ratio(text)

        

   
    summary = (
        df[df["Grade_Level"].isin(readability_levels)]
        .groupby("Grade_Level")[["Flesch_Reading_Ease", "Flesch_Kincaid_Grade", "Gunning_Fog_Index", "Type_Token_Ratio"]]
        .mean()
        .reset_index()
    )

  
    summary["Grade_Level"] = pd.Categorical(summary["Grade_Level"], categories=["5", "8", "10", "university"], ordered=True)
    summary = summary.sort_values("Grade_Level").reset_index(drop=True)
    summary["Model"] = model_name

    return df, summary


def plot_comparisons(all_summaries):
    metrics = [
        ("Flesch_Kincaid_Grade", "Flesch–Kincaid Grade Level"),
        ("Flesch_Reading_Ease", "Flesch Reading Ease Score"),
        ("Gunning_Fog_Index", "Gunning Fog Index"),
        ("Type_Token_Ratio", "Type–Token Ratio (Lexical Diversity)"),
        
    ]

    plt.style.use("seaborn-v0_8-whitegrid")
    grade_order = ["5", "8", "10", "university"]
    all_summaries["Grade_Level"] = pd.Categorical(all_summaries["Grade_Level"], categories=grade_order, ordered=True)

    for col, ylabel in metrics:
        plt.figure(figsize=(9, 5))
        sns.barplot(
            data=all_summaries,
            x="Grade_Level",
            y=col,
            hue="Model",
            hue_order=["ChatGPT", "Claude", "Gemini"],
            order=grade_order,
            edgecolor="black"
        )
        plt.title(f"Comparison of {ylabel} by Grade Level", fontsize=13, fontweight="bold")
        plt.xlabel("Target Grade Level")
        plt.ylabel(ylabel)
        plt.legend(title="Model", bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.tight_layout()
        filename = f"comparison_{col}.png"
        plt.savefig(filename, dpi=300, bbox_inches="tight")
        plt.close()



if __name__ == "__main__":
    model_files = {
        "ChatGPT": "ChatGPT_responses.xlsx",
        "Claude": "claude_responses.xlsx",
        "Gemini": "gemini_responses.xlsx"
    }

    summaries = []
    for model, path in model_files.items():
   
        _, summary = analyze_llm_responses(path, model)
        summaries.append(summary)

    all_summaries = pd.concat(summaries, ignore_index=True)

   
  

   
    plot_comparisons(all_summaries)
