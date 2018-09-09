#!/usr/bin/env python3

import datetime
import os
import sys

import pandas


# parameters

# AL's CSV records have timestamps in minute granularity
# if @smooth_seconds is set to True, then timestamps would
# be gracefully updated with seconds intervals
smooth_seconds = True

str_case_agnostic = True

def convert(filename):
    data = pandas.read_csv(filename, encoding="cp1252")

    column_name_conversions = {
        "Elapsed Dive Time (hr:min)": "sample time (min)",
        "Depth(M)":"sample depth (m)",
        "Temp.(°C)": "sample temperature (C)",
        "Pressure Reading(BAR)": "sample pressure (bar)",
    }

    data.rename(columns=column_name_conversions, inplace=True)
    df = pandas.DataFrame(data, columns=list(column_name_conversions.values()))

    seen_instances = dict()
    total_instances = df.groupby("sample time (min)").count()["sample depth (m)"]

    def conv_minutes(s):
        dt = datetime.datetime.strptime(s, "%H:%M")
        aggregated_minutes = dt.hour*60 + dt.minute
        
        if (not smooth_seconds) or (s not in seen_instances):
            seen_instances[s] = 1
            return "{}:00".format(aggregated_minutes)
        part_of_min = int(max(1, 60/total_instances[s]))
        secs = min(59, part_of_min * seen_instances[s])
        seen_instances[s] = seen_instances[s] + 1
        return ":".join(map(str, [aggregated_minutes, secs]))
        
    df["sample time (min)"] = df["sample time (min)"].apply(conv_minutes)
    
    filename_fixed = "_".join(["fixed", os.path.basename(filename)])
    df.to_csv(filename_fixed, index=False)
    return filename_fixed

def main():
    arg = None
    try:
        while arg not in ("q", "quit", "exit"):
            if arg is not None:
                try:
                    print("Generated converted file:", convert(arg))
                except FileNotFoundError:
                    print("File '{}' not found".format(arg), file=sys.stderr)
                    break
            arg = input("Enter filename to convert:")
            if str_case_agnostic and isinstance(arg, str):
                arg = arg.lower()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
