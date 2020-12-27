# IMPORT LIBRARIES
import pandas as pd
import requests

# GET ONS DATA

# The URL syntax: https://api.ons.gov.uk/dataset/{dataset_id}/timeseries/{timeseries_id}/data
timseries_ID = 'L55O'
dataset_ID = 'MM23'
URL = 'https://api.ons.gov.uk/dataset/{}/timeseries/{}/data'.format(dataset_ID, timseries_ID)
r = requests.get(URL)

# Convert to dataframe, create financial years, drop excess data
df_ONS_raw = pd.DataFrame(r.json()['months'])  # The monthly data is saved in the months part
df_ONS_raw['FY'] = df_ONS_raw.year.shift(3)  # Shift year column by 3 months to create financial years
df_ONS_raw.drop(columns=['sourceDataset', 'quarter', 'updateDate', 'label', 'date'],
                inplace=True)  # Drop superfluous columns
df_ONS_raw.FY = df_ONS_raw.FY.astype(float)  # the original data were all strings
df_ONS_raw['value'] = df_ONS_raw.value.astype(float)  # the original data were all strings
df_ONS_raw = df_ONS_raw.set_index(['FY', 'month'])  # Multi-index for clarity


# GET RESIDENTIAL RETAIL DATA

# This gets sheet names
path = r'C:\Users\Jacob\OneDrive\Python\Data Inputs\Residential Retail.xls'
xl = pd.ExcelFile(path)
water_companies = xl.sheet_names

# This concatenates data from each excel sheet. NB I assume that the sheet name is the water company name
df = pd.DataFrame()
for sheet in water_companies:
    df1 = pd.read_excel(path, sheet_name=sheet)
    df1['Company'] = sheet
    df1['Year'] = df1.FY

    df1.set_index(['Company', 'Year'], inplace=True)
    df = pd.concat([df, df1])
df.columns = df.columns.str.replace(' ', '_') # Replace spaces in column names with underscores

# SET VALUE OF THE SCALARS
Materiality_Threshold = 0.02  # Materiality Threshold
Discount_Rate = 0.035  # This is the discount rate
Conversion_Factor = 1000  # This is the £m to ,000 conversion factor

# Group (i.e. calculate the FY average) the raw ONS data and merge this into the new dataframe
s = df_ONS_raw.value.groupby(['FY']).mean()  # This takes the annual average of ONS CPI index
df_ONS_grouped = pd.DataFrame(s)  # Converts series to dataframe to allow subsequent merging

# Merge into one dataframe
df = df.reset_index()  # merge destroys the index. Reset it to send to columns, the set again
df = pd.merge(df, df_ONS_grouped, how='left', left_on=df.FY, right_on='FY')
df.set_index(['Company', 'Year'], inplace=True)


# FORECAST CPIH AFTER 2019 (the last year of full historic CPI data)
forecast_cpih = 0.02
df['CPIH_index'] = df.apply(lambda row:
                           ((1 + forecast_cpih) ** (row.FY - 2019)) * df.value.loc[df.FY == 2019].mean()
                           if row.FY > 2019
                           else row.value, axis=1)

# CALCULATE THE DIFFERENCE IN THE CPIH INDEX
df['CPIH_index_delta'] = df.CPIH_index.diff().mask(df.FY==min(df.FY))  # Take the first difference of the CPI index mask first year as else it shows difference between different companies
df['CPIH'] = df.CPIH_index_delta / df.CPIH_index.shift(1)


# CALCULATIONS

df['BYA_financing_adjustment'] = df.apply(lambda row:
                                    row.Total_Blind_Year_Adjustment *
                                    (1 + Discount_Rate) ** row.Period_Counter
                                    if (row.FY == 2024) else 0, axis=1)

df['Allowed_Revenue'] = df.Total_Revenue + \
            ((df.Actual_Customers - df.Forecast_customers) *
            df.Modification_Factor / Conversion_Factor)

df['Allowed_Revenue_RFC'] = df.Total_Revenue + \
                           ((df.Actual_Customers - df.Reforecast_Customers) *
                            df.Modification_Factor / Conversion_Factor)

df['Actual_Revenue_Net'] = df.Revenue_Recovered + df.Revenue_Sacrifice

df['Net_Adjustment'] = df.Allowed_Revenue - df.Actual_Revenue_Net

df['Net_Difference_RFC'] = df.Actual_Revenue_Net - df.Allowed_Revenue_RFC / df.Allowed_Revenue

df['Net_Difference_RFC_ABS'] = abs(df.Net_Difference_RFC)

#  is the calc below right?
df['Net_Adjustment_with_Penalty'] = df.Net_Adjustment * (1 + Discount_Rate)**df.Forecast_Period_Counter

df2 = pd.DataFrame(df[['Net_Difference_RFC_ABS', 'Net_Adjustment',
                       'Net_Adjustment_with_Penalty', 'BYA_financing_adjustment']].
                   groupby(['Company']).sum())

df2['Materiality_Threshold_breached'] = df2.Net_Difference_RFC_ABS.apply(
                                         lambda x: True if x > Materiality_Threshold
                                         else False)

df2['Net_Adjustment_to_Apply'] = df2.apply(lambda row:
                                                row.Net_Adjustment_with_Penalty
                                                if row.Materiality_Threshold_breached == True
                                                else row.Net_Adjustment, axis=1)

df2['Revenue_adjustment_at_the_end_of_AMP7'] = df2.Net_Adjustment_to_Apply + \
                                               df2.BYA_financing_adjustment

# EXPORT RESULTS
df_ONS_raw.columns = df_ONS_raw.columns.str.replace('_', ' ')
df.columns = df.columns.str.replace('_', ' ')
df2.columns = df2.columns.str.replace('_', ' ')
df_ONS_raw.to_excel(r'C:\Users\Jacob\OneDrive\Python\Data Inputs\Residential Retail ONS Raw.xlsx')
df.to_excel(r'C:\Users\Jacob\OneDrive\Python\Data Inputs\Residential Retail Output 1.xlsx')
df2.to_excel(r'C:\Users\Jacob\OneDrive\Python\Data Inputs\Residential Retail Output 2.xlsx')
