"""
The purpose of this script was to clean model responses before scoring or readability analysis.
Since a lot contained useless symbols and latex notation which could affect the test scores

Removes:
 - LaTeX/math formatting symbols (*, $, { }, etc.)
 - Arrows (\rightarrow, \leftarrow, ->)
 - Extra whitespace and redundant newlines

Running it:
    python clean_llm_responses.py --input raw_responses.xlsx --output cleaned_responses.xlsx
"""

#Need pandas and re
import pandas as pd
import re
import argparse

def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    cleaned = text

    #Remove the LaTeX style arrows (This was more common after copying and pasting from LLM conversations)
    cleaned = re.sub(r"\\rightarrow|\\leftarrow|->|<-", " to ", cleaned)

    #Remove LaTeX style braces and math symbols 
    cleaned = re.sub(r"[${}\\*]", "", cleaned)

    #Replace multiple white spaces 
    cleaned = re.sub(r"\s+", " ", cleaned)

    #Strip leading/trailing whitespace
    cleaned = cleaned.strip()

    return cleaned


def clean_dataframe(input_path: str, output_path: str = "cleaned_responses.xlsx"):
    """
    read the results 
    
    """
    df = pd.read_excel(input_path)
    df["Cleaned_Response"] = df["Model_Response"].apply(clean_text)

    # Save cleaned output
    df.to_excel(output_path, index=False)
    print(f"All done, saved to {output_path}") #Final Checker


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean LLM model responses for grading")
    parser.add_argument("--input", required=True, help="Path to Excel/CSV file with raw responses")
    parser.add_argument("--output", default="cleaned_responses.xlsx", help="Output Excel filename")
    args = parser.parse_args()
    clean_dataframe(args.input, args.output)
