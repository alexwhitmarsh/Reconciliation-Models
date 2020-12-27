import pandas as pd
import matplotlib.pyplot as plt


# ---------- IMPORT DATA FROM OUTPUTS FOLDER -----------------
df = pd.read_excel(r'C:\Users\Jacob\OneDrive\Python\Pycharm\New approach\Outputs\RFI All.xlsx')

# ---------------   DATA VISUALISATIONS  ---------------------------------------
print(df)


# LINE GRAPH

fig, (ax1, ax2) = plt.subplots(sharex=True, nrows=2, ncols=1)

ax1.set_title('Path of revenues and penalty bands')
ax1.plot(df.loc['AFW', ('Wastewater_network', 'Allowed_revenue')], label='Original Allowed Revenue',linestyle=':', color='grey' )
ax1.plot(df.loc['AFW',('Wastewater_network', 'Actual_revenue')], label='Actual revenue', linestyle=':', marker='h', color='black')
ax1.plot(df.loc['AFW',('Wastewater_network', 'Adjusted_allowed_revenue')], label='Adjusted allowed Revenue', color='blue')
ax1.fill_between(df.index, df.loc['AFW', ('Wastewater_network', 'Outer_upper_bound')],
                           df.loc['AFW', ('Wastewater_network', 'Outer_lower_bound')],
                alpha=0.7, color='blue')
ax1.fill_between(df.index, df.loc['AFW', ('Wastewater_network', 'Inner_upper_bound')],
                           df.loc['AFW', ('Wastewater_network', 'Inner_lower_bound')],
                 alpha=0.7, color='lavender')
#plt.xticks(df[('All', 'FY')])
#ax1.set_ylabel('Total revenue, £m')
ax1.legend()

"""
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

#print(df[('Wastewater_network', 'Penalty_rate_adjustment')].sum())

"""