from argparse import ArgumentParser, Namespace
from pathlib import Path
import pandas as pd


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--data_dir", type=Path, required=True)
    parser.add_argument("--output_file", type=Path, required=True)
    args = parser.parse_args()
    return args


def main():

    args = parse_args()

    # Load data
    data = pd.read_excel(args.data_file)
    processed = pd.DataFrame()
    for file in args.data_dir.iterdir():
        # Load data
        data = pd.read_excel(file, sheet_name=None)
        sheet = pd.ExcelFile(file)

        sheet_name = sheet[0]
        # Select sheet and set columns
        df = data.get(sheet_name)
        df.Admissindate = pd.to_datetime(df.Admissindate, format="%Y-%m-%d")
        # Process
        processed = pd.concat([processed, process_data(df)], ignore_index=False)

    # Save
    processed.to_excel(args.output_file, index=False)


def process_data(df: pd.DataFrame) -> pd.DataFrame:

    rtn = pd.DataFrame()
    rtn = pd.concat([rtn, process_event(df)], ignore_index=False)
    rtn = pd.concat([rtn, process_time(df)], ignore_index=False)

    return rtn


def process_event(df: pd.DataFrame) -> pd.DataFrame:

    rtn = {"aid": [], "pid": [], "prefix": [], "input_text": [], "target_text": []}

    prev_sentence = None

    for row in df.itertuples():
        # Target text
        target_text = []
        if not pd.isna(row.Remission) or not pd.isna(row.Response):
            target_text.append("Remission")
        if not pd.isna(row.Acute):
            target_text.append("Acute")
        if not pd.isna(row.DayCare):
            target_text.append("DayCare")
        if not pd.isna(row.Episode):
            target_text.append("Episode")
        if len(target_text) == 0:
            target_text = "None"
        else:
            target_text = ", ".join(target_text)
        # Merge to the previous example if the current sentence is the same as previous one
        if prev_sentence == row.Sentence:
            # Continue if no events and duplicated sentences
            if target_text == "None":
                continue
            else:
                if rtn["target_text"][-1] == "None":
                    rtn["target_text"][-1] = target_text
                else:
                    rtn["target_text"][-1] = f"{rtn['target_text'][-1]}, {target_text}"
        else:
            rtn["aid"].append(row.AID)
            rtn["pid"].append(row.PID)
            rtn["prefix"].append("event detection")
            rtn["input_text"].append(f"{row.Sentence} options: Remission, Acute, DayCare, Episode.")
            rtn["target_text"].append(target_text)
        # Store sentence
        prev_sentence = row.Sentence

    return pd.DataFrame(rtn)


def process_time(df: pd.DataFrame) -> pd.DataFrame:

    rtn = {"aid": [], "pid": [], "prefix": [], "input_text": [], "target_text": []}

    duration_head = None
    prev_sentence = None

    for row in df.itertuples():
        # Target text is None when TimeInfo column is NaN
        if pd.isna(row.TimeInfo):
            target_text = "None"
        else:
            # Target text is composed by two lines when duration is not NaN
            if not pd.isna(row.Duration):
                # Duration head
                if duration_head is None:
                    duration_head = row.Time_YMD
                    continue
                else:
                    target_text = f"duration: {duration_head} to {row.Time_YMD}"
                    duration_head = None
            else:
                target_text = []
                if not pd.isna(row.Time_YMD):
                    target_text.append(f"time: {row.Time_YMD}.")
                if not pd.isna(row.Vague) and row.Vague != "Fact":
                    target_text.append(f"vague: {row.Vague}.")
                if not pd.isna(row.Age):
                    target_text.append(f"age: {row.Age}.")
                if not pd.isna(row.Ago_YMD):
                    target_text.append(f"ago: {row.Ago_YMD}.")
                assert len(target_text) != 0, row.AID
                target_text = " ".join(target_text)

        # Merge to the previous example if the current sentence is the same as previous one
        if row.Sentence == prev_sentence:
            # Continue if no events and duplicated sentences
            if target_text == "None":
                continue
            else:
                if rtn["target_text"][-1] == "None":
                    rtn["target_text"][-1] = target_text
                else:
                    rtn["target_text"][-1] = f"{rtn['target_text'][-1]} {target_text}"
        else:
            rtn["aid"].append(row.AID)
            rtn["pid"].append(row.PID)
            rtn["prefix"].append("time extraction")
            rtn["input_text"].append(f"{row.Sentence} admission date: {row.Admissindate}. options: time, vague, age, ago.")
            rtn["target_text"].append(target_text)
        # Store sentence
        prev_sentence = row.Sentence

    return pd.DataFrame(rtn)


if __name__ == '__main__':
    main()