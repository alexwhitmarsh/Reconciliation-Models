# THIS SHEET REPLICATES THE CALCULATIONS IN THE WATER RESOURCES SHEET IN THE MODEL

import pandas as pd
import numpy as np

#  Payments to be applied this reporting year after abatements and deferrals

df = pd.DataFrame({
                                    'FY':   [2020,     2021,    2022,   2023,   2024,   2025],
             'Water_resources_K_factors':   [0,        0.03,   0.03,    0.03,   0.03,   0.03],
               'Water_network_K_factors':   [0,        0.04,   0.04,    0.04,   0.04,   0.04],
          'Wastewater_network_K_factors':   [0,        0.05,   0.05,    0.05,   0.05,   0.05],
                                  'CPIH':   [0.02,     0.02,   0.02,    0.02,   0.02,   0.02],
                     'Marginal_tax_rate':   [0,        0,       0,      0.19,   0.19,   0.19]
})
df.set_index('FY', drop=False, inplace=True)

# Generate the culmulative series based on CPIH + K
K_factors = [df.Water_resources_K_factors, df.Water_network_K_factors, df.Wastewater_network_K_factors]

for i in K_factors:
    lst = []
    z = 1
    for FY, K, CPIH in zip(df.FY, i, df.CPIH):
        if FY > 2020:
            z = z * (1 + K + CPIH)
        else: z = 1
        lst.append(z)
    df[str(i.name) + '_CPIH_K_culmulative'] = lst
print(df.tail())

# Generate the culmulative series based on CPIH
lst = []
z = 1
for FY, CPIH in zip(df.FY, df.CPIH):
    if FY > 2020:
        z = z * (1 + CPIH)
    else: z = 1
    lst.append(z)
df['CPIH_culmulative'] = lst


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

# Sets

Starting_revenue = [Water_resources, Water_network_plus, Wastewater_network_plus]


def poop(control, K_factor):
    global Year_of_adjustment_to_be_applied
    Year_of_adjustment_to_be_applied = Reporting_year + 2
    df['ODI_payment_for_this_control'] = df.FY.apply(lambda x: control # Water_resources
    if x == Year_of_adjustment_to_be_applied
    else 0)
    # REVENUE ADJUSTMENTS
    df['Allowed_revenue'] = Allowed_revenue_starting_point_in_FD * df.CPIH_K_culmulative
    df['ODI_value_nominal_price'] = df.ODI_payment_for_this_control * df.CPIH_culmulative
    # Tax adjustment
    df['Total_value_of_ODI'] = df.ODI_value_nominal_price * (1 / (1 - df.Marginal_tax_rate))
    df['Revised_total_nominal_revenue'] = df.Allowed_revenue + df.Total_value_of_ODI
    # Revised K
    df['Allowed_revenue_percentage_movement'] = df.Revised_total_nominal_revenue.pct_change()
    df['Allowed_revenue_percentage_movement_deflated'] = df.apply(lambda row: row.Allowed_revenue_percentage_movement
    if row.FY >= Year_of_adjustment_to_be_applied
    else 0, axis=1)
    df['Revised_K'] = df.Allowed_revenue_percentage_movement_deflated.round(2)  # this is simplyfied - the original calc did odd rounding up or down


poop(Water_resources)

print(df.tail())