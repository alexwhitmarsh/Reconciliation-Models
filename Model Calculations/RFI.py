import inflation as inf
import data_imports as di


def model(df):
    # ---------------- IMPORT DATA -------------------------------------------------------
    lst = ['FY', 'CPIH_FY', 'CPIH_November_index_shift1_base2019', 'CPIH_November_shift-1',
           'CPIH_November_shift-2']  # Only import the inflation variables we need

    df = df.reset_index(). \
        merge(di.RFI_scalars.reset_index(), how='left', left_on=['Company', 'Control'], right_on=['index', 'Control']). \
        merge(inf.inflation()[lst], how='left', on='FY'). \
        set_index(['Company', 'Year']). \
        pivot(columns='Control').swaplevel(axis=1)

    df.sort_index(axis=1, inplace=True)

    # SETS
    controls = ['Wastewater_network', 'Water_network', 'Water_resources']
    wholesale_controls = ['Wholesale_water', 'Wastewater_network']
    companies = df.index.get_level_values(0).unique()

    # CREATE ALL CATEGORY AND DELETE SUPERFLOUS COLUMNS
    for i in lst:
        df[('All', i)] = df[('Water_network', i)]
        for control in controls:
            df.drop(columns=[(control, i)], axis=1, inplace=True)

    for control in controls:
        df.drop(columns=[(control, 'index')], axis=1, inplace=True)

    # ----------------  CALCULATIONS  -----------------------------------------------

    for company in companies:
        for control in controls:
            lst = []
            z = 1
            for FY, K, CPIH in zip(df.loc[company, ('All', 'FY')], df.loc[company, (control, 'K_factors')],
                                   df.loc[company, ('All', 'CPIH_FY')]):
                if FY > 2020:
                    z = z * (1 + K + CPIH)
                else:
                    z = 1
                lst.append(z)
            df.loc[company, (control, 'CPIH_K_culmulative')] = lst

    for control in controls:
        df[(control, 'Allowed_revenue')] = df.apply(
            lambda row: row[(control, 'Allowed_revenue_2019')] * row[(control, 'CPIH_K_culmulative')]
            if row[('All', 'FY')] > 2020
            else 0, axis=1)

        df[(control, 'Blind_year_adjustment_profiled')] = df[(control, 'Blind_year_profiling_factor')] \
                                                          * df[(control, 'Total_blind_year_adjustment')]

        df[(control, 'Blind_year_adjustment_inc_financing_rate')] = df[(control, 'Blind_year_adjustment_profiled')] * \
                                                                    (1 + di.scalars.Discount_Rate) ** (
                                                                                df[('All', 'FY')] - 2020)

        df[(control, 'Blind_year_adjustment_inc_financing_inflation')] = df[(
        control, 'Blind_year_adjustment_inc_financing_rate')] * \
                                                                         df[(
                                                                         'All', 'CPIH_November_index_shift1_base2019')]
    # REVENUE ADJUSTMENT
    df[('Wholesale_water', 'Revenue_imbalance')] = 0
    df[('Wholesale_water', 'Adjusted_allowed_revenue')] = 0
    df[('Water_resources', 'Bilateral_entry_adjustment')] = 0  # delete when merged in other model

    for control in controls:
        df[(control, 'RFI')] = 0
        df[(control, 'Revenue_imbalance')] = 0
        df[(control, 'Adjusted_allowed_revenue')] = 0
        df[(control, 'Main_revenue_adjustment_with_financing')] = 0
        df[(control, 'Main_revenue_adjustment_financing_inflation')] = 0

    for company in companies:
        for year in df[('All', 'FY')]:
            if year > 2020:
                for control in controls:
                    if ('network' in control):
                        df.loc[(company, year), (control, 'Adjusted_allowed_revenue')] = df.loc[(company, year), (
                                                                                         control, 'Allowed_revenue')] + \
                                                                                         df.loc[(company, year), (
                                                                                         control,
                                                                                         'Blind_year_adjustment_inc_financing_inflation')] + \
                                                                                         df.loc[(company, year), (
                                                                                         control, 'RFI')]
                    else:
                        df.loc[(company, year), (control, 'Adjusted_allowed_revenue')] = df.loc[(company, year), (
                                                                                         control, 'Allowed_revenue')] + \
                                                                                         df.loc[(company, year), (
                                                                                         control,
                                                                                         'Blind_year_adjustment_inc_financing_inflation')] + \
                                                                                         df.loc[(company, year), (
                                                                                         control, 'RFI')] + \
                                                                                         df.loc[(company, year), (
                                                                                         'Water_resources',
                                                                                         'Bilateral_entry_adjustment')]

                    df.loc[(company, year), (control, 'Revenue_imbalance')] = df.loc[(company, year), (
                                                                              control, 'Adjusted_allowed_revenue')] - \
                                                                              df.loc[(company, year), (
                                                                              control, 'Actual_revenue')]

                    df.loc[(company, year), (control, 'Main_revenue_adjustment_with_financing')] = df.loc[(company,
                                                                                                           year), (
                                                                                                          control,
                                                                                                          'Revenue_imbalance')] * \
                                                                                                   ((
                                                                                                                1 + di.scalars.Discount_Rate) ** 2)

                    df.loc[(company, year), (control, 'Main_revenue_adjustment_financing_inflation')] = df.loc[(company,
                                                                                                                year), (
                                                                                                               control,
                                                                                                               'Main_revenue_adjustment_with_financing')] * \
                                                                                                        (1 + df.loc[(
                                                                                                                    company,
                                                                                                                    year), (
                                                                                                                    'All',
                                                                                                                    'CPIH_November_shift-1')]) * \
                                                                                                        (1 + df.loc[(
                                                                                                                    company,
                                                                                                                    year), (
                                                                                                                    'All',
                                                                                                                    'CPIH_November_shift-2')])

                df.loc[(company, year), ('Wholesale_water', 'Revenue_imbalance')] = df.loc[(company, year), (
                                                                                    'Water_resources', 'Revenue_imbalance')] + \
                                                                                    df.loc[(company, year), (
                                                                                    'Water_network',
                                                                                    'Revenue_imbalance')]

                df.loc[(company, year), ('Wholesale_water', 'Adjusted_allowed_revenue')] = df.loc[(company, year), (
                'Water_resources', 'Adjusted_allowed_revenue')] + \
                                                                                           df.loc[(company, year), (
                                                                                           'Water_network',
                                                                                           'Adjusted_allowed_revenue')]

                for wholesale_control in wholesale_controls:
                    df.loc[(company, year), (wholesale_control, 'Forecast_error')] = abs(
                        df.loc[(company, year), (wholesale_control, 'Revenue_imbalance')]) / \
                                                                                     df.loc[(company, year), (
                                                                                     wholesale_control,
                                                                                     'Adjusted_allowed_revenue')] \
                        if year > 2020 and year < 2026 \
                        else 0

                    df.loc[(company, year), (wholesale_control, 'Penalty_applicable')] = 1 if (df.loc[(company, year), (
                    wholesale_control, 'Forecast_error')] > di.scalars.RFI_minimum_threshold) else 0

                    df.loc[(company, year), (wholesale_control, 'Error_magnitude')] = (df.loc[(company, year), (
                    wholesale_control, 'Forecast_error')] - di.scalars.RFI_minimum_threshold) / \
                                                                                      (
                                                                                                  di.scalars.RFI_maximum_threshold - di.scalars.RFI_minimum_threshold) \
                        if df.loc[(company, year), (wholesale_control, 'Penalty_applicable')] == 1 \
                        else 0

                    df.loc[(company, year), (wholesale_control, 'PR')] = di.scalars.RFI_penalty_rate * min(
                        df.loc[(company, year), (wholesale_control, 'Error_magnitude')], 1)

                    df.loc[(company, year), (wholesale_control, 'Penalty_rate_adjustment_POS')] = abs(
                        df.loc[(company, year), (wholesale_control, 'Revenue_imbalance')]) * df.loc[(company, year), (
                    wholesale_control, 'PR')] \
                        if year > 2020 and year < 2026 \
                        else 0

                    df.loc[(company, year), (wholesale_control, 'Penalty_rate_adjustment')] = -1 * df.loc[
                        (company, year), (wholesale_control, 'Penalty_rate_adjustment_POS')]

                    df.loc[(company, year), (wholesale_control, 'Penalty_rate_adjustment_with_financing')] = df.loc[(
                                                                                                                    company,
                                                                                                                    year), (
                                                                                                                    wholesale_control,
                                                                                                                    'Penalty_rate_adjustment')] * \
                                                                                                             (
                                                                                                                         1 + di.scalars.Discount_Rate)

                    df.loc[(company, year), (wholesale_control, 'Penalty_rate_adjustment_with_financing_inflation')] = \
                    df.loc[(company, year), (wholesale_control, 'Penalty_rate_adjustment_with_financing')] * \
                    (1 + df.loc[(company, year), ('All', 'CPIH_November_shift-1')]) * \
                    (1 + df.loc[(company, year), ('All', 'CPIH_November_shift-2')])

                    df.loc[(company, year), (wholesale_control, 'Performance_variance_level_alert')] = 1 \
                        if df.loc[(company, year), (
                    wholesale_control, 'Forecast_error')] > di.scalars.RFI_threshold_for_additional_variance_analyses \
                        else 0

                    df.loc[(company, year), ('Water_resources', 'Proportion_of_penalty_allocated_to_WaterRes')] = 1 - \
                                                                                                                  df.loc[
                                                                                                                      (
                                                                                                                      company,
                                                                                                                      year), (
                                                                                                                      'Water_network',
                                                                                                                      'Proportion_of_penalty_allocated_to_WaterN')] \
                        if year > 2020 and year < 2026 \
                        else 0

                df.loc[(company, year), ('Water_resources', 'Penalty_rate_adjustment_with_financing_inflation')] = \
                df.loc[(company, year), ('Wholesale_water', 'Penalty_rate_adjustment_with_financing_inflation')] * \
                df.loc[(company, year), ('Water_resources', 'Proportion_of_penalty_allocated_to_WaterRes')]

                df.loc[(company, year), ('Water_network', 'Penalty_rate_adjustment_with_financing_inflation')] = df.loc[
                                                                                                                     (
                                                                                                                     company,
                                                                                                                     year), (
                                                                                                                     'Wholesale_water',
                                                                                                                     'Penalty_rate_adjustment_with_financing_inflation')] * \
                                                                                                                 df.loc[
                                                                                                                     (
                                                                                                                     company,
                                                                                                                     year), (
                                                                                                                     'Water_network',
                                                                                                                     'Proportion_of_penalty_allocated_to_WaterN')]

                if year <= (df[('All',
                                'FY')].max() - 2):  # This ensures that it doesn't try to create values for years outside of the dataframe
                    for control in controls:
                        df.loc[(company, year + 2), (control, 'RFI')] = df.loc[(company, year), (
                        control, 'Main_revenue_adjustment_financing_inflation')] + \
                                                                        df.loc[(company, year), (control,
                                                                                                 'Penalty_rate_adjustment_with_financing_inflation')] \
                            if year > 2020 and year < 2026 \
                            else 0

    df.sort_index(axis=1, inplace=True)

    # ADDED VARIABLES FOR FURTHER ANALYSIS

    for control in controls:
        df[(control, 'Outer_upper_bound')] = df[(control, 'Adjusted_allowed_revenue')] * (
                    1 + di.scalars.RFI_maximum_threshold)
        df[(control, 'Outer_lower_bound')] = df[(control, 'Adjusted_allowed_revenue')] * (
                    1 - di.scalars.RFI_maximum_threshold)
        df[(control, 'Inner_upper_bound')] = df[(control, 'Adjusted_allowed_revenue')] * (
                    1 + di.scalars.RFI_minimum_threshold)
        df[(control, 'Inner_lower_bound')] = df[(control, 'Adjusted_allowed_revenue')] * (
                    1 - di.scalars.RFI_minimum_threshold)

    return df


# --------------------  END MODEL  (note - this hasn't worked out the years 4 and 5 adjustments...) ---------------------

