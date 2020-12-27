import inflation as inf
import data_imports as di


def model(df):

    # Merge in the CPI data and bioresources scalars
    df = df.reset_index().\
        merge(inf.inflation(), how='left', on='FY'). \
        merge(di.bio_scalars, how='left', left_on='Company', right_index=True).\
        set_index(['Company', 'Year'])

    # ----- Calculation of average revenue control   -----
    df['discount_level_for_NPV'] = df.FY.apply(lambda x: (1 / (1 + di.scalars.Discount_Rate) ** (x - 2020)))

    df['FTDS_TDS'] = df.FTDS_TTDS * 1000

    df['FTDS_discounted'] = df.FTDS_TDS * df.discount_level_for_NPV

    df['Total_discounted_sludge'] = df.FTDS_discounted.groupby('Company').transform('sum')

    df['discounted_total_rev_requirement'] = df.Total_Bioresources_Allowance * \
                                             df.discount_level_for_NPV

    df['Total_discounted_revenue_requirement'] = df.discounted_total_rev_requirement.groupby('Company').transform('sum')

    df['standard_average_revenue_control'] = df.Total_discounted_revenue_requirement * 1000000 \
                                             / df.Total_discounted_sludge

    #  I DON'T UNDERSTAND THIS ADDITIONAL BLOCK
    #   A) the input doesn't stem from the licence
    #   B) the SAV only equates to the reconstructured_unadjusted evenue in the special case that ODI = 0

    # ---   Revenue requirement for period check   ------
    df['Unadjusted_revenue_by_year'] = df.standard_average_revenue_control * df.FTDS_TDS \
                                       / 1000000

    df['Revised_Unadjusted_revenue'] = df.Unadjusted_revenue_by_year + df.ODI

    df['Discounted_unadjusted_revenue'] = df.Unadjusted_revenue_by_year * \
                                          df.discount_level_for_NPV

    df['Reconstructed_unadjusted_revenue'] = df.Discounted_unadjusted_revenue.groupby('Company').transform('sum')

    Total_discounted_revenue_requirement_check = \
        df['Reconstructed_unadjusted_revenue'] == df['Total_discounted_revenue_requirement']

    # ---   Company fixed and variable elements of revenue adjustment   ------
    df['Revenue_to_remunerate_variables_costs_by_year'] = df.Variable_revenue * df.FTDS_TDS / \
                                                          1000000

    df['Discounted_variable_element_revenue'] = df.Revenue_to_remunerate_variables_costs_by_year * \
                                                df.discount_level_for_NPV

    df['Discounted_fixed_element_revenue'] = df.Discounted_unadjusted_revenue - \
                                             df.Discounted_variable_element_revenue

    df['Total_discounted_fixed_element_revenue'] = df.Discounted_fixed_element_revenue.\
                                                    groupby('Company').transform('sum')

    df['Total_discounted_variable_element'] = df.Discounted_variable_element_revenue.groupby('Company').transform('sum')

    df['Discounted_variable_revenue'] = df.Total_discounted_variable_element * 1000000 / \
                                        df.Total_discounted_sludge

    df['Discounted_fixed_variable'] = df.Total_discounted_fixed_element_revenue * 1000000 / \
                                      df.Total_discounted_sludge

    df['Discounted_total_average_revenue'] = df.Discounted_variable_revenue + df.Discounted_fixed_variable

    df['Fixed_element_adjustment_total_revenue_check'] = \
        round(df.Discounted_total_average_revenue) == round(df.standard_average_revenue_control)

    # ---------  Calculation of modified revenue  ------------

    df['ATDS_TDS'] = df.ATDS_TTDS * 1000

    df['Discounted_outturn_sludge'] = df.ATDS_TDS * df.discount_level_for_NPV

    df['Modified_revenue'] = df.Revised_Unadjusted_revenue + \
                             ((df.ATDS_TDS - df.FTDS_TDS) * df.Discounted_variable_revenue) / 1000000

    df['Modified_revenue_inflated'] = df.Modified_revenue * df['CPIH_November_index_base2018']

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
            df.loc[(slice(None), i), 'Allowed_revenue'] = df.loc[(slice(None), i), 'Modified_revenue_inflated'] + \
                                                          df.loc[
                                                              (slice(None), i), 'Total_adjustment_to_allowed_revenue']

        # ---------  Revenue over / under recovery

        df.loc[(slice(None), i), 'Revenue_imbalance'] = df.loc[(slice(None), i), 'Revenue_Recovered'] - \
                                                        df.loc[(slice(None), i), 'Allowed_revenue']

        df.loc[(slice(None), i), 'ABR'] = df.loc[(slice(None), i), 'Revenue_imbalance'] * (
                    (1 + di.scalars.Discount_Rate) ** 2)

        if i < 2023:
            df.loc[(slice(None), i), 'ABR_inflated'] = df.loc[(slice(None), i), 'ABR'] * \
                                                       (1 + df.loc[(slice(None), i), 'CPIH_November_shift1']) * \
                                                       (1 + df.loc[(slice(None), i), 'CPIH_November_shift2'])

        if i < 2023:
            df.loc[(slice(None), i), 'Profit_inflated'] = df.loc[(slice(None), i), 'Profit'] * \
                                                          (1 + df.loc[(slice(None), i), 'CPIH_November_shift1']) * \
                                                          (1 + df.loc[(slice(None), i), 'CPIH_November_shift2'])

        df.loc[(slice(None), i), 'Total_revenue_adjustment'] = -1 * (df.loc[(slice(None), i), 'ABR_inflated'] +
                                                                     df.loc[(slice(None), i), 'Profit_inflated'])

        if i <= (
                df.FY.max() - 2):  # This ensures that it doesn't try to create values for years outside of the dataframe

            df.loc[(slice(None), i + 2), 'Total_adjustment_to_allowed_revenue'] = df.loc[
                (slice(None), i), 'Total_revenue_adjustment']

    # -------- APPLICATION OF THE ADJUSTMENT IN LAST TWO YEARS

    # ------- Year 4 - One year of the CPIH and financing costs adjustments applied
    df['Revenue_imbalance_shift1'] = df.Revenue_imbalance.shift(1)

    df['Profit_shift1'] = df.Profit.shift(1)

    df['Value_of_year_4_ABR'] = df.apply(lambda row: -1 * row.Revenue_imbalance_shift1 *
                                                     (1 + di.scalars.Discount_Rate) *
                                                     (1 + row.CPIH_November)
                                if row.FY == 2024
                                else 0, axis=1)

    df['Value_of_year_4_Other'] = df.apply(lambda row: -1 * row.Profit_shift1 *
                                                       (1 + row.CPIH_November)
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

    return df








