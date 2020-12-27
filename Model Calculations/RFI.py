import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df_global = pd.DataFrame({
                            ('All', 'FY'):   [2020,     2021,    2022,   2023,   2024,   2025],
                            ('All', 'CPIH'): [0.02,     0.02,   0.02,    0.02,   0.02,   0.02],
     })
df_global.set_index(('All', 'FY'), drop=False, inplace=True)

# Generate the culmulative series based on CPIH
lst = []
z = 1
for FY, CPIH in zip(df_global[('All', 'FY')], df_global[('All', 'CPIH')]):
    if FY > 2020:
        z = z * (1 + CPIH)
    else: z = 1
    lst.append(z)
df_global[('All', 'CPIH_culmulative')] = lst


df_global[('All', 'CPIH_delta_shift1')] = df_global[('All', 'CPIH')].shift(-1)
df_global[('All', 'CPIH_delta_shift2')] = df_global[('All', 'CPIH')].shift(-2)


df = pd.DataFrame({
    ('All', 'FY'):                                          [2020,     2021,    2022,   2023,   2024,   2025],
    ('Water_resources', 'Bilateral_entry_adjustment'):      [0,        0,      0,       -3,     -3,       -3],
    ('Water_resources', 'K_factors'):                       [0,        0.03,   0.03,    0.03,   0.03,   0.03],
    ('Water_network', 'K_factors'):                         [0,        0.04,   0.04,    0.04,   0.04,   0.04],
    ('Wastewater_network', 'K_factors'):                    [0,        0.0,   0.0,    0.0,   0.0,   0.0],
    ('Wastewater_network', 'Actual_revenue'):               [0,        102.,    104.04,     106.1208,    108.2432,    110.4081],
    ('Water_network', 'Actual_revenue'):                    [0,        55,     60,      65,     70,     75],
    ('Water_resources', 'Actual_revenue'):                  [0,        55,     60,      65,     70,     75],
    ('Wastewater_network', 'Blind_year_profiling_factor'):  [0,        0,      0.25,    0.25,   0.25,   0.25],
    ('Water_network', 'Blind_year_profiling_factor'):       [0,        0,      0.25,    0.25,   0.25,   0.25],
    ('Water_resources', 'Blind_year_profiling_factor'):     [0,        0,      0.25,    0.25,   0.25,   0.25],
('Water_network', 'Proportion_of_penalty_allocated_to_WaterN'): [0,    0.66,    0.66,     0.66,    0.66,    0.66],
})
df.set_index(('All', 'FY'), drop=False, inplace=True)
df.sort_index(axis=1, inplace=True)




# MERGE LOCAL AND GLOBAL DATASETS

df = df.merge(df_global,left_index=True, right_index=True, suffixes=('_drop', "")).drop(columns=('All_drop', 'FY'))


#  SCALARS

discount_rate = 0.035
Minimum_threshold = 0.02
Maximum_threshold = 0.03
Penalty_rate = 0.03
Threshold_for_additional_variance_analyses = 0.06

Wastewater_Network_allowed_revenue = 100 / 1.02
Water_Network_allowed_revenue = 50
Water_resources_allowed_revenue = 50

Wastewater_Network_total_blind_year_adjustment = 0
Water_Network_total_blind_year_adjustment = 15
Water_resources_total_blind_year_adjustment = 15




# SETS
controls = ['Wastewater_network', 'Water_network', 'Water_resources']
wholesale_controls = ['Wholesale_water', 'Wastewater_network']
allowed_revenues = [Wastewater_Network_allowed_revenue, Water_Network_allowed_revenue, Water_resources_allowed_revenue]
total_blind_year_adjustments = [Wastewater_Network_total_blind_year_adjustment, Water_Network_total_blind_year_adjustment,
                                Water_resources_total_blind_year_adjustment]
K_factors = [df[('Wastewater_network', 'K_factors')], df[('Water_network', 'K_factors')], df[('Water_resources', 'K_factors')]]


# SCENARIOS

df.loc[2021, ('Wastewater_network', 'Actual_revenue')] = Wastewater_Network_allowed_revenue * 0.95 * 1.02




# CALCULATIONS

# This creates the allowed revenues and blind year adjustents for each control


for control, AR, total_blind_year_adjustment, K_factor in zip(controls, allowed_revenues, total_blind_year_adjustments, K_factors):
    lst = []
    z = 1
    for FY, K, CPIH in zip(df[('All', 'FY')], K_factor, df[('All', 'CPIH')]):
        if FY > 2020:
            z = z * (1 + K + CPIH)
        else:
            z = 1
        lst.append(z)
    df[(control, 'CPIH_K_culmulative')] = lst


    df[(control, 'Allowed_revenue')] = df.apply(lambda row: AR * row[(control, 'CPIH_K_culmulative')]
                                 if row[('All', 'FY')] > 2020
                                 else 0, axis=1)

    df[(control, 'Blind_year_adjustment_profiled')] = df[(control, 'Blind_year_profiling_factor')] \
                                                      * total_blind_year_adjustment

    df[(control, 'Blind_year_adjustment_inc_financing_rate')] = df[(control, 'Blind_year_adjustment_profiled')] * \
                                                 (1 + discount_rate) ** (df[('All', 'FY')] - 2020)

    df[(control, 'Blind_year_adjustment_inc_financing_inflation')] = df[(control, 'Blind_year_adjustment_inc_financing_rate')] * \
                                                        df[('All', 'CPIH_culmulative')]


# REVENUE ADJUSTMENT

df.loc[:, ('Water_resources', 'Revenue_imbalance')] = 0

for control in controls:
    df[(control, 'RFI')] = 0
    df[(control, 'Revenue_imbalance')] = 0
    df[(control, 'Adjusted_allowed_revenue')] = 0
    df[(control, 'Main_revenue_adjustment_with_financing')] = 0
    df[(control, 'Main_revenue_adjustment_financing_inflation')] = 0
    df[('Wholesale_water', 'Revenue_imbalance')] = 0
    df[('Wholesale_water', 'Adjusted_allowed_revenue')] = 0


for year in df[('All', 'FY')]:
    if year > 2020:
        for control in controls:
            if ('network' in control):
                df.loc[year, (control, 'Adjusted_allowed_revenue')] = df.loc[year, (control, 'Allowed_revenue')] + \
                                                                      df.loc[year, (control, 'Blind_year_adjustment_inc_financing_inflation')] + \
                                                                      df.loc[year, (control, 'RFI')]
            else:
                df.loc[year, (control, 'Adjusted_allowed_revenue')] = df.loc[year, (control, 'Allowed_revenue')] + \
                                                                      df.loc[year, (control, 'Blind_year_adjustment_inc_financing_inflation')] + \
                                                                      df.loc[year, (control, 'RFI')] + \
                                                                      df.loc[year, ('Water_resources', 'Bilateral_entry_adjustment')]

            # Scenario - endogenous allowed revenue after year 1 shoch
            df.loc[year, ('Wastewater_network', 'Actual_revenue')] = df.loc[year, ('Wastewater_network', 'Adjusted_allowed_revenue')] \
                        if df.loc[year, ('All', 'FY')] > 2021 \
                        else df.loc[year, ('Wastewater_network', 'Actual_revenue')]


            # End of scenario

            df.loc[year, (control, 'Revenue_imbalance')] = df.loc[year, (control, 'Adjusted_allowed_revenue')] - \
                                                           df.loc[year, (control, 'Actual_revenue')]

            df.loc[year, (control, 'Main_revenue_adjustment_with_financing')] = df.loc[year, (control, 'Revenue_imbalance')] * \
                                                                                ((1 + discount_rate)**2)

            df.loc[year, (control, 'Main_revenue_adjustment_financing_inflation')] = df.loc[year, (control, 'Main_revenue_adjustment_with_financing')] * \
                                                                                     (1 + df.loc[year, ('All', 'CPIH_delta_shift1')]) * \
                                                                                     (1 + df.loc[year, ('All', 'CPIH_delta_shift2')])

        df.loc[year, ('Wholesale_water', 'Revenue_imbalance')] = df.loc[year, ('Water_resources', 'Revenue_imbalance')] + \
                                                                 df.loc[year, ('Water_network', 'Revenue_imbalance')]

        df.loc[year, ('Wholesale_water', 'Adjusted_allowed_revenue')] = df.loc[year, ('Water_resources', 'Adjusted_allowed_revenue')] + \
                                                                        df.loc[year, ('Water_network', 'Adjusted_allowed_revenue')] \


    for wholesale_control in wholesale_controls:
            df.loc[year, (wholesale_control, 'Forecast_error')] = abs(df.loc[year, (wholesale_control, 'Revenue_imbalance')]) / \
                                                                  df.loc[year, (wholesale_control, 'Adjusted_allowed_revenue')] \
                                                                if year > 2020 and year < 2026 \
                                                                else 0

            df.loc[year, (wholesale_control, 'Penalty_applicable')] = 1 if df.loc[year, (wholesale_control, 'Forecast_error')] > Minimum_threshold else 0


            df.loc[year, (wholesale_control, 'Error_magnitude')] = (df.loc[year, (wholesale_control, 'Forecast_error')] - Minimum_threshold) / \
                                                                   (Maximum_threshold - Minimum_threshold) \
                                if df.loc[year, (wholesale_control, 'Penalty_applicable')] == 1 \
                                else 0

            df.loc[year, (wholesale_control, 'PR')] = Penalty_rate * min(df.loc[year, (wholesale_control, 'Error_magnitude')], 1)

            df.loc[year, (wholesale_control, 'Penalty_rate_adjustment_POS')] = abs(df.loc[year, (wholesale_control, 'Revenue_imbalance')]) * df.loc[year, (wholesale_control, 'PR')] \
                if year > 2020 and year < 2026 \
                else 0

            df.loc[year, (wholesale_control, 'Penalty_rate_adjustment')] = -1 * df.loc[year, (wholesale_control, 'Penalty_rate_adjustment_POS')]

            df.loc[year, (wholesale_control, 'Penalty_rate_adjustment_with_financing')] = df.loc[year, (wholesale_control, 'Penalty_rate_adjustment')] * \
                                                                                          (1 + discount_rate)


            df.loc[year, (wholesale_control, 'Penalty_rate_adjustment_with_financing_inflation')] = df.loc[year, (wholesale_control, 'Penalty_rate_adjustment_with_financing')] * \
                                                                                                    (1 + df.loc[year, ('All', 'CPIH_delta_shift1')]) * \
                                                                                                    (1 + df.loc[year, ('All', 'CPIH_delta_shift2')])

            df.loc[year, (wholesale_control, 'Performance_variance_level_alert')] = 1 \
                if df.loc[year, (wholesale_control, 'Forecast_error')] > Threshold_for_additional_variance_analyses \
                else 0

            df.loc[year, ('Water_resources', 'Proportion_of_penalty_allocated_to_WaterRes')] = 1 - \
                                                                                               df.loc[year, ('Water_network', 'Proportion_of_penalty_allocated_to_WaterN')] \
                if year > 2020 and year < 2026 \
                else 0

    df.loc[year, ('Water_resources', 'Penalty_rate_adjustment_with_financing_inflation')] = df.loc[year, ('Wholesale_water', 'Penalty_rate_adjustment_with_financing_inflation')] * \
                                                                                            df.loc[year, ('Water_resources', 'Proportion_of_penalty_allocated_to_WaterRes')]

    df.loc[year, ('Water_network', 'Penalty_rate_adjustment_with_financing_inflation')] = df.loc[year, ('Wholesale_water', 'Penalty_rate_adjustment_with_financing_inflation')] * \
                                                                                          df.loc[year, ('Water_network', 'Proportion_of_penalty_allocated_to_WaterN')]

    for control in controls:
        df.loc[year + 2, (control, 'RFI')] = df.loc[year, (control, 'Main_revenue_adjustment_financing_inflation')] + \
                                             df.loc[year, (control, 'Penalty_rate_adjustment_with_financing_inflation')] \
                            if year > 2020 and year < 2026 \
                            else 0


df.sort_index(axis=1, inplace=True)
df.drop([2020, 2026, 2027], inplace=True)

# END MODEL  (note - this hasn't worked out the years 4 and 5 adjustments...)

# ADDED VARIABLES FOR FURTHER ANALYSIS

for control in controls:
    df[(control, 'Outer_upper_bound')] = df[(control, 'Adjusted_allowed_revenue')] * (1 + Maximum_threshold)
    df[(control, 'Outer_lower_bound')] = df[(control, 'Adjusted_allowed_revenue')] * (1 - Maximum_threshold)
    df[(control, 'Inner_upper_bound')] = df[(control, 'Adjusted_allowed_revenue')] * (1 + Minimum_threshold)
    df[(control, 'Inner_lower_bound')] = df[(control, 'Adjusted_allowed_revenue')] * (1 - Minimum_threshold)



# DATA VISUALISATIONS

print(df.transpose())

# LINE GRAPH

fig, (ax1, ax2) = plt.subplots(sharex=True, nrows=2, ncols=1)

ax1.set_title('Path of revenues and penalty bands')
ax1.plot(df[('Wastewater_network', 'Allowed_revenue')], label='Original Allowed Revenue',linestyle=':', color='grey' )
ax1.plot(df[('Wastewater_network', 'Actual_revenue')], label='Actual revenue', linestyle=':', marker='h', color='black')
ax1.plot(df[('Wastewater_network', 'Adjusted_allowed_revenue')], label='Adjusted allowed Revenue', color='blue')
ax1.fill_between(df.index, df[('Wastewater_network', 'Outer_upper_bound')],
                           df[('Wastewater_network', 'Outer_lower_bound')],
                alpha=0.7, color='blue')
ax1.fill_between(df.index, df[('Wastewater_network', 'Inner_upper_bound')],
                           df[('Wastewater_network', 'Inner_lower_bound')],
                 alpha=0.7, color='lavender')
plt.xticks(df[('All', 'FY')])
ax1.set_ylabel('Total revenue, £m')
ax1.legend()


# BAR GRAPH
width = 0.1
ax2.set_title('Adjustment items')
ax2.bar(df.index-width*2, df[('Wastewater_network', 'Revenue_imbalance')], label='Revenue Imbalance', width=width, color='lime')
ax2.bar(df.index-width, df[('Wastewater_network', 'RFI')], label='RFI adjustment', width=width, color='limegreen')
ax2.bar(df.index, df[('Wastewater_network', 'Blind_year_adjustment_inc_financing_inflation')], label='Blind year adjustment as incurred', width=width)
ax2.bar(df.index+(width), df.loc[:,('Wastewater_network', 'Penalty_rate_adjustment')], label='Penalty rate', width=width, color='pink')
ax2.bar(df.index+2+(width*2), df.loc[:,('Wastewater_network', 'Penalty_rate_adjustment_with_financing_inflation')], label='Penalty rate as inccured', width=width, color='red')
ax2.set_ylabel('Difference in revenue, £m')
ax2.set_xlabel('Financial year ending')
ax2.legend()
#plt.savefig('RFI scenario - Yr1 shock.png')
#plt.style.use('seaborn')
plt.show()

print(df[('Wastewater_network', 'Penalty_rate_adjustment')])