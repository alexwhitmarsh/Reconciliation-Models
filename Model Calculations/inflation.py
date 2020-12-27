import requests, sys
import pandas as pd
import data_imports as di


def inflation():
        # The URL syntax: https://api.ons.gov.uk/dataset/{dataset_id}/timeseries/{timeseries_id}/data
        timseries_ID = 'L522'
        dataset_ID = 'MM23'
        URL = 'https://api.ons.gov.uk/dataset/{}/timeseries/{}/data'.format(dataset_ID, timseries_ID)
        r = requests.get(URL)

        # Convert to dataframe, create financial years, drop excess data
        df = pd.DataFrame(r.json()['months'])  # The monthly data is saved in the months part
        df['FY'] = df.year.shift(3)  # Shift year column by 3 months to create financial years

        df.FY = df.FY.astype(float)  # the original data were all strings
        df['ONS_data'] = df.value.astype(float)  # the original data were all strings
        df.drop(columns=['sourceDataset', 'quarter', 'updateDate', 'label', 'date', 'value'],
                inplace=True)  # Drop superfluous columns
        df = df.set_index(['FY', 'month'])  # Multi-index for clarity
        print(df)

        # This isn't really a groupby as the slice takes one value per year, i.e. the value in November. It's quick way of dropping columns to get the right format
        November_inflation = df.loc[(slice(None),'November'),:].groupby(['FY']).mean()
        print(November_inflation)

        annualised_inflation = df.ONS_data.groupby(['FY']).mean()  # This takes the annual average of ONS CPI index
        ONS_grouped = pd.merge(November_inflation, annualised_inflation,how='outer',left_on='FY', right_on='FY')
        ONS_grouped.columns = ['ONS_FY_average', 'ONS_November']

        # Create an empty dataframe covering the years we want
        df = pd.DataFrame({'FY': list(range(2015, 2028))})

        # merge the annualised inflation into the new data frame
        df = pd.merge(df, ONS_grouped, how='left', left_on='FY', right_on='FY')

        # FORECAST CPIH AFTER 2019 (the last year of full historic CPI data)
        df['CPIH_FY_index'] = df.apply(lambda row:
                                    ((1 + di.scalars.Forecast_CPIH) ** (row.FY - 2019)) * df.ONS_FY_average.loc[
                                            df.FY == 2019].mean()
                                    if row.FY > 2019
                                    else row.ONS_FY_average, axis=1)

        df['CPIH_November_index'] = df.apply(lambda row:
                                       ((1 + di.scalars.Forecast_CPIH) ** (row.FY - 2019)) * df.ONS_November.loc[
                                               df.FY == 2019].mean()
                                       if row.FY > 2019
                                       else row.ONS_November, axis=1)



        df['CPIH_November_index_base2018'] = df['CPIH_November_index'] / \
                                             df.loc[df['FY']==2018, 'CPIH_November_index'].values



        # CALCULATE THE DIFFERENCE IN THE CPIH INDEX
        df['CPIH_FY_index_delta'] = df.CPIH_FY_index.diff().mask(df.FY == min(
                df.FY))  # Take the first difference of the CPI index mask first year as else it shows difference between different companies

        df['CPIH_November_index_delta'] = df.CPIH_November_index.diff().mask(df.FY == min(
                df.FY))  # Take the first difference of the CPI index mask first year as else it shows difference between different companies

        df['CPIH_FY'] = df.CPIH_FY_index_delta / df.CPIH_FY_index.shift(1)

        df['CPIH_November'] = df.CPIH_November_index_delta / df.CPIH_November_index.shift(1)

        df['CPIH_November_shift-1'] = df.CPIH_November.shift(-1)

        df['CPIH_November_shift-2'] = df.CPIH_November.shift(-2)

        df['CPIH_November_index_shift1'] = df.CPIH_November_index.shift(1)

        df['CPIH_November_index_shift1_base2019'] = df.CPIH_November_index_shift1 / \
                                             df.loc[df['FY']==2019, 'CPIH_November_index'].values

        return df



#---------------- OPTIONAL: EXPORT TO EXCEL ----------------------

df = inflation()
print(df)


sys.exit()

df_export = df
df_export.columns = df_export.columns.str.replace('_', ' ')
df_export.to_excel(r'C:\Users\Jacob\OneDrive\Python\Pycharm\New approach\Outputs\Inflation.xlsx')


