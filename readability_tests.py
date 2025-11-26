"""
Grading score version 2
grading and readability testing for LLM  responses.
Measures:
-TTR
-Flesch-Kincaid Grade Level
-Gunning Fog Index
-Correctness
Need: pandas, textstat, re

"""

import pandas as pd
import textstat
import re


def type_token_ratio(text):
    """ype-Token Ratio (TTR) = unique words / total words 
    cite: https://www.sketchengine.eu/glossary/type-token-ratio-ttr/#:~:text=The%20type/token%20ratio%2C%20often,This%20sentence:
    """ 
    tokens = re.findall(r'\b\w+\b', str(text).lower())
    if len(tokens) == 0:
        return 0
    unique_tokens = set(tokens)
    return round(len(unique_tokens) / len(tokens), 3)


def check_correctness(row):
    """Check correctness for yes and no and multiple choice responses"""
    if pd.isna(row.get("Correct_Answer")) or pd.isna(row.get("Model_Response")):
        return None
    correct = str(row["Correct_Answer"]).strip().lower()
    response = str(row["Model_Response"]).strip().lower()
   


   
    response = re.sub(r'[^a-z0-9]', '', response)
    correct = re.sub(r'[^a-z0-9]', '', correct)
    return 1 if correct in response else 0


def analyze_llm_responses(excel_path, export_path=None):
    df = pd.read_excel(excel_path)
    readability_levels = {"5", "8", "10", "university"}

    df["Flesch_Reading_Ease"] = None
    df["Flesch_Kincaid_Grade"] = None
    df["Gunning_Fog_Index"] = None
    df["Type_Token_Ratio"] = None
    df["Correctness"] = None





    for idx, row in df.iterrows():
        grade = str(row.get("Grade_Level")).strip().lower() if not pd.isna(row.get("Grade_Level")) else None
        text = str(row.get("Model_Response"))

    
        if grade in readability_levels:
            df.at[idx, "Flesch_Reading_Ease"] = textstat.flesch_reading_ease(text)
            df.at[idx, "Flesch_Kincaid_Grade"] = textstat.flesch_kincaid_grade(text)
            df.at[idx, "Gunning_Fog_Index"] = textstat.gunning_fog(text)
            df.at[idx, "Type_Token_Ratio"] = type_token_ratio(text)

        if not pd.isna(row.get("Correct_Answer")):
            df.at[idx, "Correctness"] = check_correctness(row)


    summary = (
        df.groupby(["Task_ID", "Variant", "Grade_Level"], dropna=False)[
            ["Flesch_Reading_Ease", "Flesch_Kincaid_Grade", "Gunning_Fog_Index", "Type_Token_Ratio", "Correctness"]
        ]
        .mean()
        .reset_index()
    )

    print("\n=== Summary (Averages per Task Variant) ===\n") #Checker in terminal for debugging
    print(summary.round(2))


    if export_path:
        with pd.ExcelWriter(export_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Full_Results", index=False)
            summary.to_excel(writer, sheet_name="Summary", index=False)
        print(f"\ncomplete and  saved to: {export_path}") #Final checker

    return df, summary











if __name__ == "__main__":
    input_file = "claude_responses.xlsx"  
    output_file = "claude_analysis_output.xlsx"
    full_df, summary_df = analyze_llm_responses(input_file, export_path=output_file)
