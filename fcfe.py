import numpy as np
import matplotlib.pyplot as plt
import pandas as pd 


#Extracting netincome
Net_Income = "your forecasted net income"

#Extracting Depreciation and amoritisation 

DandA = 'forecasted d&A'

#Extracting the Capex

Capex = ' forecaste Capex'

#extracting foreccasteed items

total_assets = 'forecaste assets'

#extracting the debt

Total_debts = 'forecast debts'

forecasted_data = 'your forecasted data'#or all you can use all of the line items above 

# Function to calculate change in net working capital (NWC)
def calculate_nwc(current_assets, current_liabilities):
    return current_assets - current_liabilities

# Calculate change in NWC for each year
change_in_nwc = [calculate_nwc(forecasted_data['Current_Assets'][i], forecasted_data['Current_Liabilities'][i])
                 - calculate_nwc(forecasted_data['Current_Assets'][i - 1], forecasted_data['Current_Liabilities'][i - 1])
                 for i in range(1, len(forecasted_data['Current_Assets']))]

# Calculate CFO for each year
cfo = [forecasted_data['Net_Income'][i] + forecasted_data['DandA'][i] - change_in_nwc[i - 1]
       for i in range(1, len(forecasted_data['Net_Income']))]

# Calculate FCF for each year (assuming FCF = CFO - Capex)
fcf = [cfo[i] - forecasted_data['Capex'][i] for i in range(len(cfo))]

# Output CFO and FCF for each year
for year, cfo_value, fcf_value in zip(range(1, len(cfo) + 1), cfo, fcf):
    print(f"Year {year}: CFO = {cfo_value}, FCF = {fcf_value}")

# Calculate FCFE for each year (FCFE = FCF - Net Borrowing)
fcfe = [fcf[i] - forecasted_data['Net_Borrowing'][i] for i in range(len(fcf))]

# Output FCFE for each year
for year, fcfe_value in zip(range(1, len(fcfe) + 1), fcfe):
    print(f"Year {year}: FCFE = {fcfe_value}")








