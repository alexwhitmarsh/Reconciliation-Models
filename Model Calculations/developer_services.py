import pandas as pd

water = pd.DataFrame({
    'FY':           [2021,  2022,   2023,   2024,   2025],
    'FC':           [100,   100,    100,    100,    100],
    'AC':           [110,   120,    130,    140,    150],
    'Unit_rate':     [1,     1,      1,      1,      1]
})

wastewater = pd.DataFrame({
    'FY':           [2021,  2022,   2023,   2024,   2025],
    'FC':           [100,   100,    100,    100,    100],
    'AC':           [110,   120,    130,    140,    150],
    'Unit_rate':     [1,     1,      1,      1,      1]
})

#  SCALARS

discount_rate = 0.035
units_in_thousands = 1_000
units_in_millions = 1_000_000


#  CALCULATIONS
df2 = pd.DataFrame()                                                # Initialise dataframe to hold the combined datasets
controls, names = [water, wastewater], ['water', 'wastewater']      # Create sets of dataframes and names of dataframes
for control, name in zip(controls, names):                          # Create for loop to loop through dataframes and names
    df = control                                                    # Load in the dataframe
    df['Control'] = name                                            # Create a column set to the control's name so we can refer to it later
    df['Difference'] = df.AC - df.FC
    df['DSRA'] = df.Unit_rate * df.Difference * units_in_thousands / units_in_millions
    df['DSRA_with_financing_adjustment'] = df.DSRA * (1 + discount_rate) ** (2025 - df.FY)
    df2 = df2.append(df)                                            # Append the dataframe to df2 before looping around again
df2.set_index(['Control', 'FY'], inplace=True)                      # Set multi index for clarity

# Sum all across all the years
df_outputs = df2.groupby(['Control']).sum().DSRA_with_financing_adjustment

print(df_outputs)