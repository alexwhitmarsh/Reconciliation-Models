import ofwat_functions as of


# -------------    GET RESIDENTIAL RETAIL TIME SERIES DATA   --------------------------------

residential_df = of.shock_overlay(r'C:\Users\Jacob\OneDrive\Python\Pycharm\New approach\Core Data\Residential Retail.xlsx',
                                  r'C:\Users\Jacob\OneDrive\Python\Pycharm\New approach\Data Overwite\Residential Retail Shock.xlsx')


# -------------    GET BIORESOURCES TIME SERIES DATA   --------------------------------

bioresources_df = of.shock_overlay(r'C:\Users\Jacob\OneDrive\Python\Pycharm\New approach\Core Data\Bioresources.xlsx',
                                   r'C:\Users\Jacob\OneDrive\Python\Pycharm\New approach\Data Overwite\Bioresources Shock.xlsx')


# ---------     GET SCALARS  -----------------------------------

scalars = of.shock_common_scalars_overlay(r"C:\Users\Jacob\OneDrive\Python\Pycharm\New approach\Core Data\Scalars.xlsx",
                                           r"C:\Users\Jacob\OneDrive\Python\Pycharm\New approach\Data Overwite\Scalars Shock.xlsx")


# ---------     GET COMPANY SCALARS FOR THE BIORESOURCES MODEL  -----------------------------------

bio_scalars = of.shock_scalars_overlay(r"C:\Users\Jacob\OneDrive\Python\Pycharm\New approach\Core Data\Scalars.xlsx",
                                                 r"C:\Users\Jacob\OneDrive\Python\Pycharm\New approach\Data Overwite\Scalars Shock.xlsx",
                                                 'bioresources')

# ---------     GET COMPANY SCALARS FOR THE RFI MODEL  -----------------------------------

RFI_scalars = of.shock_scalars_overlay(r"C:\Users\Jacob\OneDrive\Python\Pycharm\New approach\Core Data\Scalars.xlsx",
                                                 r"C:\Users\Jacob\OneDrive\Python\Pycharm\New approach\Data Overwite\Scalars Shock.xlsx",
                                                 'RFI')


RFI_df = of.shock_overlay(r'C:\Users\Jacob\OneDrive\Python\Pycharm\New approach\Core Data\RFI.xlsx',
                          r'C:\Users\Jacob\OneDrive\Python\Pycharm\New approach\Data Overwite\RFI Shock.xlsx')





