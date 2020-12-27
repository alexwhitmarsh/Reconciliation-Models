import pandas as pd
import data_imports as di


# -----------   CALCULATIONS   -------------------------------------------------

def model(df):
    df['BYA_financing_adjustment'] = df.apply(lambda row:
                                              row.Total_Blind_Year_Adjustment *
                                              (1 + di.scalars.loc['Discount_Rate']) ** row.Period_Counter
                                              if (row.FY == 2024) else 0, axis=1)

    df['Allowed_Revenue'] = df.Total_Revenue + \
                            ((df.Actual_Customers - df.Forecast_customers) *
                             df.Modification_Factor / di.scalars.loc['Conversion_Factor'])

    df['Allowed_Revenue_RFC'] = df.Total_Revenue + \
                                ((df.Actual_Customers - df.Reforecast_Customers) *
                                 df.Modification_Factor / di.scalars.loc['Conversion_Factor'])

    df['Actual_Revenue_Net'] = df.Revenue_Recovered + df.Revenue_Sacrifice

    df['Net_Adjustment'] = df.Allowed_Revenue - df.Actual_Revenue_Net

    df['Net_Difference_RFC'] = df.Actual_Revenue_Net - df.Allowed_Revenue_RFC / df.Allowed_Revenue

    df['Net_Difference_RFC_ABS'] = abs(df.Net_Difference_RFC)

    df['Net_Adjustment_with_Penalty'] = df.Net_Adjustment * (1 + di.scalars.loc['Discount_Rate']) ** df.Forecast_Period_Counter

    df2 = pd.DataFrame(df[['Net_Difference_RFC_ABS', 'Net_Adjustment',
                           'Net_Adjustment_with_Penalty', 'BYA_financing_adjustment']].
                       groupby(['Company']).sum())

    df2['Materiality_Threshold_breached'] = df2.Net_Difference_RFC_ABS.apply(
        lambda x: True if x > di.scalars.loc['Materiality_Threshold']
        else False)

    df2['Net_Adjustment_to_Apply'] = df2.apply(lambda row:
                                               row.Net_Adjustment_with_Penalty
                                               if row.Materiality_Threshold_breached == True
                                               else row.Net_Adjustment, axis=1)

    df2['Revenue_adjustment_at_the_end_of_AMP7'] = df2.Net_Adjustment_to_Apply + \
                                                   df2.BYA_financing_adjustment

    return df, df2

#-------------     END      -----------------------------------

