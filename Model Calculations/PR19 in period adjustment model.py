# THIS SHEET REPLICATES THE CALCULATIONS IN THE WATER RESOURCES SHEET IN THE MODEL

import pandas as pd
import numpy as np

#  Payments to be applied this reporting year after abatements and deferrals

df = pd.DataFrame({
                                    'FY':   [2020,     2021,    2022,   2023,   2024,   2025],
#'Allowed_revenue_starting_point_in_FD':    [100,      0,       0,      0,      0,      0],
                             'K_factors':   [0,        0.03,   0.03,    0.03,   0.03,   0.03],
                              'CPIH':       [0.02,     0.02,   0.02,    0.02,   0.02,   0.02],
                 'Marginal_tax_rate':       [0,        0,       0,      0.19,   0.19,   0.19]
})
df.set_index('FY', drop=False, inplace=True)

# Generate the culmulative series based on CPIH + K
lst = []
z = 1
for FY, K, CPIH in zip(df.FY, df.K_factors, df.CPIH):
    if FY > 2020:
        z = z * (1 + K + CPIH)
    else: z = 1
    lst.append(z)
df['CPIH_K_culmulative'] = lst

# Generate the culmulative series based on CPIH
lst = []
z = 1
for FY, CPIH in zip(df.FY, df.CPIH):
    if FY > 2020:
        z = z * (1 + CPIH)
    else: z = 1
    lst.append(z)
df['CPIH_culmulative'] = lst

print(lst)


#  Scalars
Allowed_revenue_starting_point_in_FD = 100

Water_resources = 10
Water_network_plus = 11
Wastewater_network_plus = 12
Bioresources_sludge = 13
Residential_retail = 14
Business_retail = 15
Dummy_control = 16

Reporting_year = 2021



#  WATER RESOURCES

# ODI PAYMENT

Year_of_adjustment_to_be_applied = Reporting_year + 2
df['ODI_payment_for_this_control'] = df.FY.apply(lambda x: Water_resources
                                                 if x == Year_of_adjustment_to_be_applied
                                                 else 0)

# REVENUE ADJUSTMENTS

df['Allowed_revenue'] = Allowed_revenue_starting_point_in_FD * df.CPIH_K_culmulative

df['ODI_value_nominal_price'] = df.ODI_payment_for_this_control * df.CPIH_culmulative

# Tax adjustment

df['Tax_on_geogetric_uplift'] = 1 / ( 1 - df.Marginal_tax_rate) - 1

df['Tax_on_nominal_ODI'] = df.ODI_value_nominal_price * df.Tax_on_geogetric_uplift

df['Total_value_of_ODI'] =  df.ODI_value_nominal_price + df.Tax_on_nominal_ODI

df['Revised_total_nominal_revenue'] = df.Allowed_revenue + df.Total_value_of_ODI

# Revised K

df['Allowed_revenue_percentage_movement'] = df.Revised_total_nominal_revenue.pct_change()

df['Year_that_price_limits_should_be_recalculated'] = df.FY.apply(lambda x: 1
                                                               if x >= Year_of_adjustment_to_be_applied
                                                               else 0)

df['Allowed_revenue_percentage_movement_deflated'] = (df.Allowed_revenue_percentage_movement - CPIH) 

df['Revised_K'] = df.Allowed_revenue_percentage_movement_deflated.round(2) # this is simplyfied - the original calc did odd rounding up or down


print(df.tail())
