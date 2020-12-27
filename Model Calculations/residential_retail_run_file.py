import data_imports as di
import residential_retail


#------   RUN THE RETAIL MODEL WITH THE OVERWRITE DATA --------------------------------
df_all, df_output = residential_retail.model(di.residential_df)


#--------- EXPORT THE UNDERLYING RETAIL DATA AND CALCULATIONS ---------------------------------
df_all.columns = df_all.columns.str.replace('_', ' ')
df_all.to_excel(r'C:\Users\Jacob\OneDrive\Python\Pycharm\New approach\Outputs\Residential Retail Model ALL.xlsx')

#--------- EXPORT THE ULTIMATE RETAIL OUTPUTS ------------------------------------------------
df_output.columns = df_output.columns.str.replace('_', ' ')
df_output.to_excel(r'C:\Users\Jacob\OneDrive\Python\Pycharm\New approach\Outputs\Residential Retail Model SUMMARY.xlsx')





df_output.describe()
df_output.info(memory_usage='deep')
print(df_all, df_output)

