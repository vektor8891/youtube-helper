#!/usr/bin/env python

import pandas as pd
import openpyxl as xl


def get_export_info(df: pd.DataFrame, f_path: str, sheet_name: str):
    info = f'{len(df.index)} rows exported to tab {sheet_name} in {f_path}'
    return info


def export_sheet(df: pd.DataFrame, sheet_name: str, f_path: str):
    writer = pd.ExcelWriter(f_path, engine='openpyxl')
    writer.book = xl.load_workbook(filename=f_path)
    writer.sheets = {ws.title: ws for ws in writer.book.worksheets}
    df.to_excel(writer, sheet_name=sheet_name, index=False)
    writer.save()
    export_info = get_export_info(df=df, f_path=f_path, sheet_name=sheet_name)
    print(export_info)
