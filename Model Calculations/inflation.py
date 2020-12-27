
# THIS FILE IS SUPERCEEDED IN SO FAR AS MOST OF IT WAS INCORPORATED INTO RESIDENTIAL RETAIL MODEL

import pandas as pd
import requests


# The URL syntax is as follows: https://api.ons.gov.uk/dataset/{dataset_id}/timeseries/{timeseries_id}/data
timseries_ID = 'D7BT'
dataset_ID = 'MM23'
URL = 'https://api.ons.gov.uk/dataset/{}/timeseries/{}/data'.format(dataset_ID, timseries_ID)
r = requests.get(URL)

# Convert to dataframe, create financial years, drop excess data
df_ONS_raw = pd.DataFrame(r.json()['months'])  # The monthly data is saved in the months part
df_ONS_raw['FY'] = df_ONS_raw.year.shift(3)  # Shift year column by 3 months to create financial years
df_ONS_raw.drop(columns=['sourceDataset', 'quarter', 'updateDate', 'label', 'date'],
                inplace=True)  # Drop superfluous columns
df_ONS_raw.FY = df_ONS_raw.FY.astype(float)
df_ONS_raw['value'] = df_ONS_raw.value.astype(float)  # the original data were all strings
df_ONS_raw = df_ONS_raw.set_index(['FY', 'month'])  # Multi-index for clarity
print(df_ONS_raw.tail())

# Create an empty dataframe to allow space for a forecast period
df_cpi = pd.DataFrame([], index=range(2009, 2031))

# Group (i.e. calculate the FY average) the raw ONS data and merge this into the new dataframe
s = df_ONS_raw.value.groupby(['FY']).mean()  # This takes the annual average
df_ONS_grouped = pd.DataFrame(s)  # Converts the new series dataframe to allow subsequent merging
df_cpi = pd.merge(df_cpi, df_ONS_grouped, how='left', left_on=df_cpi.index, right_on='FY')

# FORECAST CPI AND ADD IT INTO THE NEW DATAFRAME
forecast_cpi = 0.02
forecast = []
for i, v in zip(df_cpi.value, df_cpi.FY):
    if v <= 2019:
        x = i
    else:
        x += x * forecast_cpi
    forecast.append(x)
series = pd.Series(forecast, name='CPI_index')
df_cpi = pd.concat([df_cpi, series], axis=1)

# CALCULATE THE DIFFERENCE IN THE CPI INDEX
df_cpi['CPI_delta'] = (df_cpi.CPI_index.diff())  # Take the first difference of the CPI index
df_cpi['CPI_delta_pct'] = df_cpi.CPI_delta / df_cpi.CPI_index.shift(1)
print(df_cpi)




