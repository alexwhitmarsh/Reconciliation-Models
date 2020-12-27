import pandas as pd

anglian = pd.DataFrame({
    'Unadjusted_revenue_by_year':   [93.078,    93.953,     94.796,     95.621,     98.848],
    'FTDS_TDS':                     [156.441,  157.911,     159.329,    160.716,    166.139]
    })

VR = 313.375  # Thi is the variable revenue

df = pd.DataFrame({
    'FY':                           [2020, 2021, 2022, 2023, 2024],
    'year':                         [2020, 2021, 2022, 2023, 2024],
    'forecast_period_flag':         [1,    1,    1,    1,   1],
    'FTDS_TTDS':                    [100,  100,  100,  100,  100],
    'Total_bioresources_allowance': [2000, 2000, 2000, 2000, 2000],
    'ODI':                          [1,    1,    1,     1,    1],
    'ATDS_TTDS':                    [100,  101,  102,   103,  104],
    'CPIH_Nov':                     [1.0658,	    1.0871, 	1.1089, 	1.1311, 	1.1537],
    'Revenue_recovered':            [2200,    2200,   2200,   2200,   2200],
    'Profit':                       [3,    3,    3,     3,    3]
})
df.set_index('year', inplace=True)   # note - set drop = false to keep FY as column still, so can delete year

df['CPIH_delta'] = df.CPIH_Nov.pct_change()
df['CPIH_delta_shift1'] = df.CPIH_delta.shift(-1)
df['CPIH_delta_shift2'] = df.CPIH_delta.shift(-2)

discount_rate = 0.035
units_in_thousands = 1000
units_to_millions = 1000000
variable_revenue = 1


# ----- Calculation of average revenue control   -----

df['discount_level_for_NPV'] = df.FY.apply(lambda x: (1/(1+discount_rate)**(x - 2020)))
df['FTDS_TDS'] = df.FTDS_TTDS * units_in_thousands
df['FTDS_discounted'] = df.FTDS_TDS * df.discount_level_for_NPV
Total_discounted_sludge = df.FTDS_discounted.sum()

df['discounted_total_rev_requirement'] = df.Total_bioresources_allowance * \
                                         df.discount_level_for_NPV
Total_discounted_revenue_requirement = df.discounted_total_rev_requirement.sum()
standard_average_revenue_control = (Total_discounted_revenue_requirement * units_to_millions)\
                                   / Total_discounted_sludge

#  I DON'T UNDERSTAND THIS ADDITIONAL BLOCK
#   A) the input doesn't stem from the licence
#   B) the SAV only equates to the reconstructured_unadjusted evenue in the special case that ODI = 0

# ---   Revenue requirement for period check   ------

df['Unadjusted_revenue_by_year'] = standard_average_revenue_control * df.FTDS_TDS\
                                   / units_to_millions
df['Revised_Unadjusted_revenue'] = df.Unadjusted_revenue_by_year + df.ODI
df['Discounted_unadjusted_revenue'] = df.Unadjusted_revenue_by_year * \
                                      df.discount_level_for_NPV
Reconstructed_unadjusted_revenue = df.Discounted_unadjusted_revenue.sum()
Total_discounted_revenue_requirement_check = \
    Reconstructed_unadjusted_revenue == Total_discounted_revenue_requirement


# ---   Company fixed and variable elements of revenue adjustment   ------

df['Revenue_to_remunerate_variables_costs_by_year'] = variable_revenue * df.FTDS_TDS / \
                                                      units_to_millions
df['Discounted_variable_element_revenue'] = df.Revenue_to_remunerate_variables_costs_by_year * \
                                            df.discount_level_for_NPV
df['Discounted_fixed_element_revenue'] = df.Discounted_unadjusted_revenue - \
                                         df.Discounted_variable_element_revenue
Total_discounted_fixed_element_revenue = df.Discounted_fixed_element_revenue.sum()
Total_discounted_variable_element = df.Discounted_variable_element_revenue.sum()
Discounted_variable_revenue = Total_discounted_variable_element * units_to_millions / \
                              Total_discounted_sludge
Discounted_fixed_variable = Total_discounted_fixed_element_revenue * units_to_millions / \
                            Total_discounted_sludge
Discounted_total_average_revenue = Discounted_variable_revenue + Discounted_fixed_variable
Fixed_element_adjustment_total_revenue_check = \
    round(Discounted_total_average_revenue) == round(standard_average_revenue_control)


# ---------  Calculation of modified revenue  ------------

df['ATDS_TDS'] = df.ATDS_TTDS * units_in_thousands
df['Discounted_outturn_sludge'] = df.ATDS_TDS * df.discount_level_for_NPV
df['Modified_revenue'] = df.Revised_Unadjusted_revenue + \
                         ((df.ATDS_TDS - df.FTDS_TDS) * Discounted_variable_revenue) / units_to_millions
df['Modified_revenue_inflated'] = df.Modified_revenue * df.CPIH_Nov


# ----------  Allowed revenue - application of an in-period revenue correction  --------
df['Allowed_revenue'] = 0
df['Revenue_imbalance'] = 0
df['ABR'] = 0
df['ABR_inflated'] = 0
df['Profit_inflated'] = 0
df['Total_revenue_adjustment'] = 0
df['Total_adjustment_to_allowed_revenue'] = 0

for i in df.FY:
    if i > 2019:
        df.loc[i, 'Allowed_revenue'] = df.loc[i, 'Modified_revenue_inflated'] + \
                                       df.loc[i, 'Total_adjustment_to_allowed_revenue']

# ---------  Revenue over / under recovery

    df.loc[i, 'Revenue_imbalance'] = df.loc[i, 'Revenue_recovered'] - \
                                     df.loc[i, 'Allowed_revenue']

    df.loc[i, 'ABR'] = df.loc[i, 'Revenue_imbalance'] * ((1 + discount_rate) ** 2)

    if i < 2023:
        df.loc[i, 'ABR_inflated'] = df.loc[i, 'ABR'] * \
                                   (1 + df.loc[i, 'CPIH_delta_shift1']) * \
                                   (1 + df.loc[i, 'CPIH_delta_shift2'])

    if i < 2023:
        df.loc[i, 'Profit_inflated'] = df.loc[i, 'Profit'] * \
                                      (1 + df.loc[i, 'CPIH_delta_shift1']) * \
                                      (1 + df.loc[i, 'CPIH_delta_shift2'])

    df.loc[i, 'Total_revenue_adjustment'] = -1 * (df.loc[i, 'ABR_inflated'] +
                                                 df.loc[i, 'Profit_inflated'])

    df.loc[i+2, 'Total_adjustment_to_allowed_revenue'] = df.loc[i, 'Total_revenue_adjustment']


# -------- APPLICATION OF THE ADJUSTMENT IN LAST TWO YEARS

# ------- Year 4 - One year of the CPIH and financing costs adjustments applied

df['Revenue_imbalance_shift1'] = df.Revenue_imbalance.shift(1)
df['Profit_shift1'] = df.Profit.shift(1)

df['Value_of_year_4_ABR'] = df.apply(lambda row: -1 * row.Revenue_imbalance_shift1 *
                                                 (1 + discount_rate) *
                                                 (1 + row.CPIH_delta)
                                     if row.FY == 2024
                                     else 0, axis=1)

df['Value_of_year_4_Other'] = df.apply(lambda row: -1 * row.Profit_shift1 *
                                                   (1 + row.CPIH_delta)
                                     if row.FY == 2024
                                     else 0, axis=1)

df['Value_of_year_4_total'] = df.Value_of_year_4_ABR + \
                              df.Value_of_year_4_Other


# ----- Year 5 - No CPI or financing adjustments applied

df['Value_of_year_5_total'] = df.apply(lambda row: -1 * (row.Profit + row.Revenue_imbalance)
                                       if row.FY == 2024
                                       else 0, axis=1)

df['Total_bioresources_revenue_adjustment'] = df['Value_of_year_4_total'] + \
                                              df['Value_of_year_5_total']

df.drop([2025, 2026], inplace=True)

# -------  PRINT OUT OUTPUTS  ---------------------------

print(df.Total_bioresources_revenue_adjustment)
print(df.transpose())
print('Total discounted sludge: ', Total_discounted_sludge)
print('Total_discounted_revenue_requirement: ', Total_discounted_revenue_requirement)
print('standard_average_revenue_control: ', standard_average_revenue_control)
print('Reconstructed_unadjusted_revenue: ', Reconstructed_unadjusted_revenue)
print('Total_discounted_revenue_requirement_check: ', Total_discounted_revenue_requirement_check)
print('Total_discounted_fixed_element_revenue: ', Total_discounted_fixed_element_revenue)
print('Total_discounted_variable_element: ', Total_discounted_variable_element)
print('Discounted_variable_revenue: ', Discounted_variable_revenue)
print('Discounted_fixed_variable: ', Discounted_fixed_variable)
print('Discounted_total_average_revenue: ', Discounted_total_average_revenue)
print('Fixed_element_adjustment_total_revenue_check: ', Fixed_element_adjustment_total_revenue_check)
