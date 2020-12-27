
import pandas as pd

# Manipulate the data frame
df = pd.read_excel('PR19-blind-year-ODI-difference-model-1.xlsx', sheet_name='Python')
df.columns = df.columns.str.replace(' ', '_')
df.set_index('When', inplace=True, drop=False)
df['Revenue_boolean'] = 'Revenue'
df['Revenue_boolean'] = df.Revenue_boolean.where(df.When.str.contains('revenue'), other='RCV')

# Set scalars
Retail_price_index_2012_13_financial_year_average = 244.675
Retail_price_index_2017_18_financial_year_average = 274.908

Factor_to_inflate_from_2012_13_prices_to_2017_18_prices = Retail_price_index_2017_18_financial_year_average /      \
                                                          Retail_price_index_2012_13_financial_year_average

# Calculations
df['Blind_year_difference_in_1213'] = df.Actual_ODI_payments - df.ODI_payments_as_at_FD

df2 = pd.DataFrame(                                                                               # Convert this into a dataframe to enable later calculations
        df.groupby(['Revenue_boolean','Control']).sum())                                          # Sum up the two revenue-related ODI figures

df2['Blind_year_difference_in_1718'] = df2.Blind_year_difference_in_1213 * Factor_to_inflate_from_2012_13_prices_to_2017_18_prices #  Inflate to the right price base

print(df2)






