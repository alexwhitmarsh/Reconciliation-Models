import pandas as pd
import requests
import matplotlib.pyplot as plt

timseries_ID = 'D7BT'
dataset_ID = 'MM23'
URL = 'https://api.ons.gov.uk/dataset/{}/timeseries/{}/data'.format(dataset_ID, timseries_ID)
r = requests.get(URL)

df_CPI = pd.DataFrame(r.json()['months'])  # The monthly data is saved in the months part
df_CPI['CPI_index'] = df_CPI.value.astype(float)
df_CPI.drop(columns=['sourceDataset', 'quarter', 'updateDate', 'label',  'value'],
                inplace=True)
print(df_CPI)

timseries_ID = 'L522'
dataset_ID = 'MM23'
URL = 'https://api.ons.gov.uk/dataset/{}/timeseries/{}/data'.format(dataset_ID, timseries_ID)
r = requests.get(URL)

df_CPIH = pd.DataFrame(r.json()['months'])  # The monthly data is saved in the months part
df_CPIH['CPIH_index'] = df_CPIH.value.astype(float)
df_CPIH.drop(columns=['sourceDataset', 'quarter', 'updateDate', 'label', 'value'],
                inplace=True)
print(df_CPIH)

df = pd.merge(df_CPIH, df_CPI, on=['year', 'month', 'date'])

df['CPIH'] = df.CPIH_index.diff()
df['CPI'] = df.CPI_index.diff()
df['CPIH_lag'] = df.CPIH.shift(-1)
df['CPIH_lag2'] = df.CPIH.shift(-2)
df['CPI_error'] = df.CPI - df.CPIH
df['CPIH_lag_error'] = df.CPIH_lag - df.CPIH
df['CPIH_lag_error2'] = df.CPIH_lag2 - df.CPIH


print(df)

plt.plot(df.date, df.CPIH_lag_error2, label = 'lag2')
plt.plot(df.date, df.CPIH_lag_error, label = 'lag')
plt.plot(df.date, df.CPI_error, label = 'CPI')
plt.legend()
plt.show()