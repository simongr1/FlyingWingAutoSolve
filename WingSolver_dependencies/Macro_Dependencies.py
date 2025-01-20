
import FreeCAD
import re
from itertools import groupby
import pandas as pd

def numeric_key(item):
         # Helper function to extract numeric part for sorting
        letter, num = item[0], int(item[1:])
        return letter, num

def extract_data(FreeCADSheet,sorted_array):
        data=[]
        #The array has the following form: [['A1','A2',...],['B1','B2',...],...]
        for row in sorted_array:
            data_row=[]
            for cell in row:
                res=FreeCADSheet.get(cell)
                data_row.append(res)
            data.append(data_row)
        return data

def spreadsheet_to_csv(spreadsheet,destination_path):
    cell_regex = re.compile('^[A-Z]+[0-9]+$')
    get_cells = lambda sheet: filter(cell_regex.search, sheet.PropertiesList)

    cell_names=[]
    for cell in get_cells(spreadsheet):
        cell_names.append(cell)
        

    # Sort items
    sorted_items = sorted(cell_names, key=numeric_key)

    # Group by leading letter
    grouped_items = [list(group) for _, group in groupby(sorted_items, key=lambda x: x[0])]

    data=extract_data(spreadsheet,grouped_items)
    df=pd.DataFrame(data)
    dfT=df.T
    dfT.to_csv(destination_path,index=False, header=False)
    print("Finished")