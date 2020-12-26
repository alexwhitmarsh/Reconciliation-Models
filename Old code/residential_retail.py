# RESIDENTIAL RETAIL MODEL

# LOAD LIBRARIES

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# IMPORT DATA
df = pd.read_excel(r'C:\Users\Nattha\OneDrive\Desktop\Residential Retail.xls')
#df.set_index('FY' , inplace=True)

model_year = np.arange(1,15)

# SET VALUE OF THE SCALARS
Materiality_Threshold = 0.02  # Materiality Threshold
Discount_Rate = 0.035 # This is the discount rate
Conversion_Factor = 1000 # This is the £m to ,000 conversion factor
Blind_Year_Adjustment = 0.5 # This is the blind year adjustment for the company

# CALCULATIONS

df['CPI'] = df['CPIH Index Nov'].diff() / 100 

df['Allowed_Revenue'] = df['Total Revenue'] + (( df['Actual Customers'] - df['Forecast customers'] ) * df['Modification Factor'] / Conversion_Factor ) 

df['CMEX'] = df['CMEX Adjustment'] * ((1 + Discount_Rate)**2) * ((1 + df['CPI'])**2) 

df['CMEX lagged'] = df['CMEX'].shift(2)

df['BY Profiled'] = Blind_Year_Adjustment * df['BY Profiling Factor'] * ( (1 + Discount_Rate)**df['Period Counter']) 

df['Adjusted Allowed Revenue'] = df['Allowed_Revenue'] + df['CMEX lagged'] + df['BY Profiled']

df['Allowed_Revenue_FC'] = df['Total Revenue'] + ( ( df['Actual Customers'] - df['Reforecast Customers'] ) * df['Modification Factor'] / Conversion_Factor )

df['Adjusted Allowed Revenue FC'] = df['Allowed_Revenue_FC'] + df['CMEX lagged'] + df['BY Profiled']

df['Net Revenue Recovered'] = df['Revenue Recovered'] + df['Revenue Sacrifice']

df['Effective Over-recovery'] = df['Adjusted Allowed Revenue'] - df['Net Revenue Recovered']

Effective_Over_Recovery_Sum = ( df['Net Revenue Recovered'].sum() - df['Adjusted Allowed Revenue FC'].sum()) / df['Adjusted Allowed Revenue'].sum()

Effective_Over_Recovery_Sum_ABS = abs(Effective_Over_Recovery_Sum)

if Effective_Over_Recovery_Sum_ABS > Materiality_Threshold:
    print("Materiality Threshold Breached!")
else:
    print ("Materiality Threshold NOT Breached")
    

# GRAPHS
    
plt.plot(df['Allowed_Revenue'])
plt.plot(df['CMEX lagged'])
plt.plot(df['BY Profiled'])