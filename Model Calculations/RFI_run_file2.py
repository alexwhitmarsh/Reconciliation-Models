import data_imports as di
import RFI

df = RFI.model(di.RFI_df)
df.describe()
df.info(memory_usage='deep')
print(df.transpose())

#--------- EXPORT THE UNDERLYING RFI DATA AND CALCULATIONS ---------------------------------
df.to_excel(r'C:\Users\Jacob\OneDrive\Python\Pycharm\New approach\Outputs\RFI All.xlsx')

df = df.swaplevel(axis=1).stack().reset_index()  # PowerBI doesn't deal well with multi-indexes, so kick everything back into columns to makre itmore readdable
df.to_excel(r'C:\Users\Jacob\OneDrive\Python\Pycharm\New approach\Outputs\RFI All Unstacked.xlsx')

