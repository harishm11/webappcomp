from read_n_format_jobdata import read_n_format
from read_n_format_jobdata import format_output_data
import pandas as pd
import numpy as np



def create_table(row_list,column_names):
    #row_list.sort(key = lambda x:(str_2_num(x[0]),x[1]))
    if len(row_list) >= 1:
        new_table = row_list
    else:
        row_data = (" ", "No Differences", " ", " ")
        row_list.append(row_data)
        new_table = row_list
    return pd.DataFrame(new_table,columns=column_names)

def Do_Compare_Auto(job1, job2, job2fname):

    col_names = job1.columns.tolist()
    job1_data, job1_num, eff_date1 = read_n_format(job1, col_names)
    if job2fname not in ('', ' ', None):
        col_names = job2.columns.tolist()
        job2_data, job2_num, eff_date2 = read_n_format(job2, col_names)
    else:
        column_names = job1_data.columns
        job2_data = pd.DataFrame(columns=column_names)
        job2_num = 'N/A'
        eff_date2 = 'N/A'

    job2_data.rename(columns={
                                 'Rating_input_value1' : 'Rating_input_value2',
                                 'Factor_Value_1':'Factor_Value_2'},inplace=True)

    merged = pd.merge(job1_data, job2_data, indicator=True, how='outer')

    merged["Factor_Matched_ind"] = merged.Factor_Value_1 == merged.Factor_Value_2
    merged["Input_Matched_ind"] = merged.Rating_input_value1.str.lower() == merged.Rating_input_value2.str.lower()

    Factor_match_fiter = merged.Factor_Matched_ind == False
    Input_mismatch_filter = merged.Input_Matched_ind == False

    filter1 = Factor_match_fiter & Input_mismatch_filter
    policy_data = (merged[filter1].loc[:, ['Rate_Table_Description', 'Driver_Name', 'VIN', 'Rating_Input_name1'
                                              , 'Rating_input_value1', 'Rating_input_value2']]).drop_duplicates()


    driver_filter = policy_data.Driver_Name.notnull()

    driver_level_data = (
    policy_data[driver_filter].loc[:, ['Rate_Table_Description', 'Driver_Name', 'Rating_Input_name1',
                                       'Rating_input_value1', 'Rating_input_value2']]).drop_duplicates()


    format_category = 'driver'
    row_list, cap_list = format_output_data(driver_level_data, format_category, job2fname)
    column_names = ('Driver Info', 'Rating variable', 'Job 1: ' + str(job1_num) + " Eff: "+  str(eff_date1), 'Job 2: ' + str(job2_num) + " Eff: "+  str(eff_date2))
    driver_table = create_table(row_list,column_names)

    vin_filter = policy_data.VIN.notnull()
    vin_empty = policy_data.VIN.isnull()
    driver_empty = policy_data.Driver_Name.isnull()
    vin_drv_filter = vin_empty & driver_empty
    policy_level_data_filter = vin_filter | vin_drv_filter

    policy_level_data = (
    policy_data[policy_level_data_filter].loc[:, ['Rate_Table_Description', 'VIN', 'Rating_Input_name1',
                                                  'Rating_input_value1', 'Rating_input_value2']]).drop_duplicates()



    policy_level_data = policy_level_data.sort_values(by=['VIN', 'Rating_Input_name1'], ascending=False)

    format_category = 'policy'
    row_list, cap_list = format_output_data(policy_level_data, format_category, job2fname)

    column_names = ('Policy Info', 'Rating variable', 'Job 1: ' + str(job1_num) + " Eff: "+  str(eff_date1), 'Job 2: ' + str(job2_num) + " Eff: "+  str(eff_date2))
    policy_table = create_table(row_list,column_names)

    format_category = 'vehicle'
    row_list, cap_list = format_output_data(policy_level_data, format_category, job2fname)

    column_names = ('Vehicle Info', 'Rating variable', 'Job 1: ' + str(job1_num) + " Eff: "+  str(eff_date1), 'Job 2: ' + str(job2_num) + " Eff: "+  str(eff_date2))
    vehicle_table = create_table(row_list,column_names)
    column_names = ('Cap Info', 'Rating variable', 'Job 1: ' + str(job1_num) + " Eff: " + str(eff_date1),
                    'Job 2: ' + str(job2_num) + " Eff: " + str(eff_date2))
    cap_table = create_table(cap_list,column_names)

    Factor_match_fiter = merged.Factor_Matched_ind == False
    Input_mismatch_filter = merged.Input_Matched_ind == True

    filter1 = Factor_match_fiter & Input_mismatch_filter
    factor_mismatch_list = (merged[filter1].loc[:, ['Rate_Table_Description']]).drop_duplicates().values.tolist()

    Factor_match_fiter = merged.Factor_Matched_ind == True
    Input_mismatch_filter = merged.Input_Matched_ind == False
    driver_filter = policy_data.Driver_Name.notnull()
    driver_level_Data_filter = driver_filter & Input_mismatch_filter & Factor_match_fiter

    driver_mismatch_list = (
    merged[driver_level_Data_filter].loc[:, 'Rate_Table_Description']).drop_duplicates().values.tolist()

    policy_level_data_filter = Input_mismatch_filter & Factor_match_fiter


    policy_mismatch_list = (
    merged[policy_level_data_filter].loc[:, 'Rate_Table_Description']).drop_duplicates().values.tolist()

    row_list = []
    addntl_data= []
    row_data = ("Factor Difference but Data Matching", " ", " ", " ")
    row_list.append(row_data)
    addntl_data.append(row_data)

    x=0
    for i in factor_mismatch_list:
        if (i not in driver_mismatch_list) and (i not in policy_mismatch_list):
            row_data = (" ", np.squeeze(i), " ", " ")
            row_list.append(row_data)
            addntl_data.append(row_data)
            x=x+1

    if x == 0 and job2_num != 'N/A':
       row_data = (" ", "No Differences", " ", " ")
       row_list.append(row_data)
       addntl_data.append(row_data)

    row_data = ("Data Difference but Factors Matching", " ", " ", " ")
    row_list.append(row_data)
    addntl_data.append(row_data)

    x=0
    for i in driver_mismatch_list:
        if (i not in factor_mismatch_list):
            row_data = (" ", np.squeeze(i), " ", " ")
            row_list.append(row_data)
            addntl_data.append(row_data)
            x = x + 1

    for i in policy_mismatch_list:
        if (i not in factor_mismatch_list):
            row_data = (" ", np.squeeze(i), " ", " ")
            row_list.append(row_data)
            addntl_data.append(row_data)
            x = x + 1

    if x == 0 and job2_num != 'N/A':
        row_data = (" ", "No Differences", " ", " ")
        row_list.append(row_data)
        addntl_data.append(row_data)

    column_names = ('Misc Info', 'Rating variable', 'Job 1: ' + str(job1_num) + " Eff: "+  str(eff_date1), 'Job 2: ' + str(job2_num) + " Eff: "+  str(eff_date2))
    misc_table = create_table(addntl_data,column_names)


    print("successful completion")

    return driver_table, policy_table,vehicle_table, misc_table, cap_table
