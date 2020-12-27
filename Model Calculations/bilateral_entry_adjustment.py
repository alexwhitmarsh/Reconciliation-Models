import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#dfx = pd.read_sql_table('Pokemon', r'C:\Users\Jacob\OneDrive\Python\Data Inputs\MySQLiteDatabase')

# IMPORT DATA

# THis gets sheet names
path = r'C:\Users\Jacob\OneDrive\Python\Data Inputs\Bilateral Entry Adjustment.xlsx'
xl = pd.ExcelFile(path)
water_companies = xl.sheet_names

# This concatenates data from each excel sheet. NB I assume that the sheet name is the water company name

df = pd.DataFrame()
for sheet in water_companies:
    df1 = pd.read_excel(path, sheet_name=sheet)
    df1['Company'] = sheet
    df1.set_index(['Company', 'WRZ_name', 'FY'], inplace=True)
    df = pd.concat([df,df1])

df['TCC'] = df.ICC + df.BCCf

df['Total_ICC_BCCa'] = df.ICC + df.BCCa

df['BEF'] = df.apply(lambda row:
                     min(row.TCC / row.Total_ICC_BCCa - 1, 0)
                     if row.Total_ICC_BCCa > 0
                     else 0, axis=1)

df['BEA'] = df.ICC * df.AUC * df.BEF


# Sum up the Bilateral entry adjustment for each company in each year, i.e. across each WRZ
df2 = df.BEA.groupby(['Company', 'FY']).sum().unstack()


print(df.head(45))
print(df2)

df2.plot.bar()
plt.xticks([1,2,3,4,5])

plt.show()