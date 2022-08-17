import xlsxwriter
import pandas as pd
import pandas as pd
import json

workbook = xlsxwriter.Workbook("site-1.xlsx")
worksheet_1 = workbook.add_worksheet("Site-1")

with open("monitor_logs.json") as f:
    data = json.load(f)

row = 0
# col = 0
for k,val in data["site-1"].items():
    col = 0
    worksheet_1.write(row,col,k)
    col += 1
    for i,j in val.items():
        worksheet_1.write(row,col,i)
        col += 1
    row += 1

for k,val in data["site-1"].items():
    for dev,log in val.items():
        name = f"{k}_{dev}"
        worksheet = workbook.add_worksheet(name)
        count = 0
        check = False
        for i in log:
            if dev == "log":
                spli_i = i.split()
                if len(spli_i) > 2:
                    if " ".join([i.split()[0],i.split()[1]]) == "Log Buffer":
                        check = True
                        continue
                if check == True and i != "":
                        worksheet.write(count,0,i)
                        count += 1
            else:
                worksheet.write(count,0,i)
                count += 1

row = 0
for k,val in data["site-1"].items():
    col = 1
    for dev,log in val.items():
        sheet_name = f"{k}_{dev}"
        worksheet_1.write_url(row,col,f"internal:'{sheet_name}'!A1", string=dev)
        col += 1
    row += 1

workbook.close()
