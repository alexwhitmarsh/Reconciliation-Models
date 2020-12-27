import pandas as pd


df = pd.DataFrame({
                                    'FY':   [2020,     2021,    2022,   2023,   2024,   2025],
             'Water_resources_K_factors':   [0,        0.03,   0.03,    0.03,   0.03,   0.03],
               'Water_network_K_factors':   [0,        0.04,   0.04,    0.04,   0.04,   0.04],
          'Wastewater_network_K_factors':   [0,        0.05,   0.05,    0.05,   0.05,   0.05],
                                  'CPIH':   [0.021,     0.015,   0.02,    0.02,   0.02,   0.02],
                        'Actual_revenue':   [0,        110,    120,     130,    140,    150],
'Wastewater_Network_Blind_year_profiling_factor':   [0,        0,      0.25,    0.25,   0.25,   0.25],
'Water_Network_Blind_year_profiling_factor':        [0,        0,      0.25,    0.25,   0.25,   0.25],
'Water_resources_Blind_year_profiling_factor':      [0,        0,      0.25,    0.25,   0.25,   0.25]
})
df.set_index('FY', drop=False, inplace=True)

df['CPIH_delta_shift1'] = df.CPIH.shift(-1)
df['CPIH_delta_shift2'] = df.CPIH.shift(-2)




# Generate the culmulative series based on CPIH
lst = []
z = 1
for FY, CPIH in zip(df.FY, df.CPIH):
    if FY > 2020:
        z = z * (1 + CPIH)
    else: z = 1
    lst.append(z)
df['CPIH_culmulative'] = lst


#  SCALARS

discount_rate = 0.035
Minimum_threshold = 0.02
Maximum_threshold = 0.03
Penalty_rate = 0.03
Threshold_for_additional_variance_analyses = 0.06

Wastewater_Network_allowed_revenue = 100
Water_Network_allowed_revenue = 50
Water_resources_allowed_revenue = 50

Wastewater_Network_total_blind_year_adjustment = 15
Water_Network_total_blind_year_adjustment = 15
Water_resources_total_blind_year_adjustment = 15


# SETS
controls = ['Wastewater_Network', 'Water_Network', 'Water_resources']
allowed_revenues = [Wastewater_Network_allowed_revenue, Water_Network_allowed_revenue, Water_resources_allowed_revenue]
total_blind_year_adjustments = [Wastewater_Network_total_blind_year_adjustment, Water_Network_total_blind_year_adjustment,
                                Water_resources_total_blind_year_adjustment]
K_factors = [df.Water_resources_K_factors, df.Water_network_K_factors, df.Wastewater_network_K_factors]


# CALCULATIONS

# This creates the allowed revenues and blind year adjustents for each control


# Generate the culmulative series based on CPIH + K


for control, AR, total_blind_year_adjustment, i in zip(controls, allowed_revenues, total_blind_year_adjustments, K_factors):


    df[control + '_Allowed_revenue'] = df.apply(lambda row: AR * row.Wastewater_network_K_factors_CPIH_K_culmulative
                                 if row.FY > 2020
                                 else 0, axis=1)


    df[control + '_Blind_year_adjustment_profiled'] = df[control + '_Blind_year_profiling_factor'] * total_blind_year_adjustment

    df[control + '_Blind_year_adjustment_inc_financing_rate'] = df[control + '_Blind_year_adjustment_profiled'] * \
                                                 (1 + discount_rate) ** (df.FY- 2020)

    df[control + '_Blind_year_adjustment_inc_financing_inflation'] = df[control + '_Blind_year_adjustment_inc_financing_rate'] * \
                                                        df['CPIH_culmulative']

    lst = []
    z = 1
    for FY, K, CPIH in zip(df.FY, i, df.CPIH):
        if FY > 2020:
            z = z * (1 + K + CPIH)
        else:
            z = 1
        lst.append(z)
    df[control + '_CPIH_K_culmulative'] = lst


# REVENUE ADJUSTMENT

df['RFI'] = 0


for i in df.FY:
    if i > 2020:
        df.loc[i, 'Adjusted_allowed_revenue'] = df.loc[i, 'Wastewater_Network_Allowed_revenue'] +\
                                         df.loc[i, 'Blind_year_adjustment_inc_financing_inflation'] +\
                                         df.loc[i, 'RFI']

        df.loc[i, 'Revenue_imbalance'] = df.loc[i, 'Adjusted_allowed_revenue'] - df.loc[i, 'Actual_revenue']

        df.loc[i, 'Main_revenue_adjustment_with_financing'] = df.loc[i, 'Revenue_imbalance'] * ((1 + discount_rate)**2)

        df.loc[i, 'Main_revenue_adjustment_financing_inflation'] = df.loc[i, 'Main_revenue_adjustment_with_financing'] *\
                                                            (1 + df.loc[i, 'CPIH_delta_shift1']) *\
                                                            (1 + df.loc[i, 'CPIH_delta_shift2'])

        df.loc[i, 'Forecast_error'] = abs(df.loc[i, 'Revenue_imbalance']) / df.loc[i, 'Adjusted_allowed_revenue']

        df.loc[i, 'Penalty_applicable'] = 1 if df.loc[i, 'Forecast_error'] > Minimum_threshold else 0

        df.loc[i, 'Error_magnitude'] = (df.loc[i,'Forecast_error'] - Minimum_threshold) / \
                                (Maximum_threshold - Minimum_threshold) \
                                if df.loc[i, 'Penalty_applicable'] == 1 \
                                else 0

        df.loc[i, 'PR'] = Penalty_rate * min(df.loc[i, 'Error_magnitude'], 1)

        df.loc[i, 'Penalty_rate_adjustment_POS'] = abs(df.loc[i, 'Revenue_imbalance']) * df.loc[i,'PR'] \
                                                   if (df.loc[i, 'FY'] > 2020) & (df.loc[i, 'FY'] < 2026) \
                                                   else 0

        df.loc[i, 'Penalty_rate_adjustment'] = -1 * df.loc[i, 'Penalty_rate_adjustment_POS']

        df.loc[i, 'Penalty_rate_adjustment_with_financing'] = df.loc[i, 'Penalty_rate_adjustment'] * (1 + discount_rate)

        df.loc[i, 'Penalty_rate_adjustment_with_financing_inflation'] = df.loc[i, 'Penalty_rate_adjustment_with_financing'] *\
                                                                 (1 + df.loc[i, 'CPIH_delta_shift1']) *\
                                                                 (1 + df.loc[i, 'CPIH_delta_shift2'])

        df.loc[i, 'Performance_variance_level_alert'] = 1 \
                                        if df.loc[i, 'Forecast_error'] > Threshold_for_additional_variance_analyses \
                                        else 0

        df.loc[i+2, 'RFI'] = df.loc[i, 'Main_revenue_adjustment_financing_inflation'] + \
                           df.loc[i, 'Penalty_rate_adjustment_with_financing_inflation'] \
                         if (df.loc[i, 'FY'] > 2020) & (df.loc[i, 'FY'] < 2026) \
                         else 0




print(df.Adjusted_allowed_revenue)