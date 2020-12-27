import data_imports as di
import bioresources


df = bioresources.model(di.bioresources_df)


# -------  PRINT OUT OUTPUTS  ---------------------------
df.describe()
df.info(memory_usage='deep')
print(df.transpose())
print('Total discounted sludge: ', df.Total_discounted_sludge.max())
print('Total_discounted_revenue_requirement: ', df.Total_discounted_revenue_requirement.max())
print('standard_average_revenue_control: ', df.standard_average_revenue_control.max())
print('Reconstructed_unadjusted_revenue: ', df.Reconstructed_unadjusted_revenue.max())
#print('Total_discounted_revenue_requirement_check: ', df.Total_discounted_revenue_requirement_check.max()
print('Total_discounted_fixed_element_revenue: ', df.Total_discounted_fixed_element_revenue.max())
print('Total_discounted_variable_element: ', df.Total_discounted_variable_element.max())
print('Discounted_variable_revenue: ', df.Discounted_variable_revenue.max())
print('Discounted_fixed_variable: ', df.Discounted_fixed_variable.max())
print('Discounted_total_average_revenue: ', df.Discounted_total_average_revenue.max())
print('Fixed_element_adjustment_total_revenue_check: ', df.Fixed_element_adjustment_total_revenue_check.max())