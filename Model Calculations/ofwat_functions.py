import pandas as pd

# ----  THIS COMPILES TIMESERIES DATA ACROSS AN EXCEL WORKBOOK

def load_dfs(path):
    """This function i) grabs the sheet names from the excel file, ii) loads that sheet's data,
    iii) concatenates this into a mega-dataframe, iv) sets the index to the sheet(i.e. company) name and year,
    v) tidies the column heading by ensuring spaces are replaced by underscores."""

    xl = pd.ExcelFile(path)
    sheet_names = xl.sheet_names
    df_data = pd.DataFrame()
    for sheet in sheet_names:
        df1 = pd.read_excel(path, sheet_name=sheet)
        df1['Company'] = sheet
        df1['Year'] = df1.FY
        df1.set_index(['Company', 'Year'], inplace=True)
        df_data = pd.concat([df_data, df1])
    df_data.columns = df_data.columns.str.replace(' ', '_')
    return df_data


def shock_common_scalars_overlay(main_scalars, shock_scalars):
    """This function over-writes the core data with any data you want to over-write it with."""
    main_df = pd.read_excel(main_scalars, sheet_name='global', squeeze=True, header=None, index_col=0)  # This forces it to be a series of the right shape
    shock_df = pd.read_excel(shock_scalars, sheet_name='global', squeeze=True, header=None, index_col=0)
    df= shock_df.combine_first(main_df)
    return df


def shock_scalars_overlay(main_scalars, shock_scalars, worksheet):
    main_df = pd.read_excel(main_scalars, sheet_name=worksheet, index_col=0)  # This forces it to be a series of the right shape
    shock_df = pd.read_excel(shock_scalars, sheet_name=worksheet, index_col=0)  # This forces it to be a series of the right shape
    df = shock_df.combine_first(main_df)
    return df


def shock_overlay(main_data, shock_data):
    main_df = load_dfs(main_data)
    shock_df = load_dfs(shock_data)
    df = shock_df.combine_first(main_df)
    return df