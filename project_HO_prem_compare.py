
from read_n_format_HO_jobdata import ho_read_n_format
from read_n_format_HO_jobdata import format_output_data
import pandas as pd
import numpy as np

def create_table(row_list,column_names):
    #row_list.sort('Rating variable')
    if len(row_list) >= 1:
        new_table = row_list
    else:
        row_data = (" ", "No Differences", " ", " ")
        row_list.append(row_data)
        new_table = row_list
    return pd.DataFrame(new_table,columns=column_names)

def Do_Compare_Home(job1, job2, job2fname):

    col_names = job1.columns.tolist()
    job1_data, no_of_slices_job1, job1_num, eff_date1 = ho_read_n_format(job1, col_names)
    if job2fname not in ('', ' ', None):
        col_names = job2.columns.tolist()
        job2_data, no_of_slices_job2,job2_num, eff_date2 = ho_read_n_format(job2, col_names)
    else:
        column_names = job1_data.columns
        job2_data = pd.DataFrame(columns=column_names)
        job2_num = 'N/A'
        eff_date2 = 'N/A'


    #job1_data['Factor_Value_1'] = job1_data['Factor_Value_1'].astype(float)
    job2_data.rename(columns={
        'Rating_input_value1': 'Rating_input_value2',
        'Factor_Value_1': 'Factor_Value_2'}, inplace=True)
    #job2_data['Factor_Value_2'] = job2_data['Factor_Value_2'].astype(float)


    merged = pd.merge(job1_data, job2_data, indicator=True, how='outer')

    merged["Factor_Matched_ind"] = merged.Factor_Value_1 == merged.Factor_Value_2
    merged["Input_Matched_ind"] = merged.Rating_input_value1.str.lower() == merged.Rating_input_value2.str.lower()


    slice_filter = merged.Slices == 1

    Factor_match_fiter = merged.Factor_Matched_ind == False
    Input_mismatch_filter = merged.Input_Matched_ind == False

    filter1 = slice_filter & Factor_match_fiter & Input_mismatch_filter
    policy_level_data = (merged[filter1].loc[:, ['Rate_Table_Description', 'Peril_Name', 'Rating_Input_name1'
                                                    , 'Rating_input_value1', 'Rating_input_value2']]).drop_duplicates()


    format_category = 'policy'
    row_list, cap_list = format_output_data(policy_level_data, format_category)
    column_names = ('Policy Info', 'Rating variable', 'Job 1: ' + str(job1_num) + " Eff: "+  str(eff_date1), 'Job 2: ' + str(job2_num) + " Eff: "+  str(eff_date2))
    policy_table = create_table(row_list,column_names)

    column_names = ('Cap Info', 'Rating variable', 'Job 1: ' + str(job1_num) + " Eff: " + str(eff_date1),
                    'Job 2: ' + str(job2_num) + " Eff: " + str(eff_date2))
    cap_table = create_table(cap_list, column_names)

    factor_n_input_list = policy_level_data.loc[:, ['Rating_Input_name1']].drop_duplicates().values.tolist()

    slice_filter = merged.Slices == 1
    Factor_match_fiter = merged.Factor_Matched_ind == False
    Input_mismatch_filter = merged.Input_Matched_ind == True

    filter1 = slice_filter & Factor_match_fiter & Input_mismatch_filter
    factor_mismatch_list = (merged[filter1].loc[:, ['Rate_Table_Description']]).drop_duplicates().values.tolist()

    slice_filter = merged.Slices == 1
    Factor_match_fiter = merged.Factor_Matched_ind == True
    Input_mismatch_filter = merged.Input_Matched_ind == False

    filter1 = slice_filter & Factor_match_fiter & Input_mismatch_filter
    policy_mismatch_list = (merged[filter1].loc[:, ['Rate_Table_Description']]).drop_duplicates().values.tolist()

    row_list = []

    row_data = ("Factor Difference but Data Matching", " ", " ", " ")
    row_list.append(row_data)
    x = 0
    for i in factor_mismatch_list:
        if (i not in policy_mismatch_list
                and i not in factor_n_input_list):
            row_data = (" ", np.squeeze(i), " ", " ")
            row_list.append(row_data)
            x=x+1

    if x == 0 and job2_num != 'N/A':
       row_data = (" ", "No Differences", " ", " ")
       row_list.append(row_data)

    row_data = ("Data Difference but Factors Matching", " ", " ", " ")
    row_list.append(row_data)
    x = 0
    for i in policy_mismatch_list:
        if (i not in factor_n_input_list
                and i not in factor_mismatch_list):
            row_data = (" ", np.squeeze(i), " ", " ")
            row_list.append(row_data)
            x = x + 1

    if x == 0 and job2_num != 'N/A':
       row_data = (" ", "No Differences", " ", " ")
       row_list.append(row_data)
    column_names = ('Misc Info', 'Rating variable', 'Job 1: ' + str(job1_num) + " Eff: "+  str(eff_date1), 'Job 2: ' + str(job2_num) + " Eff: "+  str(eff_date2))
    addt_table = create_table(row_list,column_names)


    slice_header = []
    slice_no = 1
    if no_of_slices_job1 > 1:
        for i in range(no_of_slices_job1 - 1):

            job1_filter = job1_data.Slices == slice_no
            no_cap_premium_filter = job1_data['Rate_Table_Description'] != 'Capped'
            data_slice1 = job1_data[job1_filter & no_cap_premium_filter]
            slice_no = slice_no + 1
            job1_slice2_filter = job1_data.Slices == slice_no
            data_slice2 = job1_data[job1_slice2_filter & no_cap_premium_filter]

            data_slice2.rename(columns={
                'Rating_input_value1': 'Rating_input_value2',
                'Factor_Value_1': 'Factor_Value_2'}, inplace=True)

            merged_slice = pd.merge(data_slice1, data_slice2,
                                    on=('Rate_Table_Description', 'Peril_Name', 'Rating_Input_name1',
                                        ),
                                    indicator=True, how='outer')


            merged_slice["Factor_Matched_ind"] = merged_slice.Factor_Value_1 == merged_slice.Factor_Value_2
            merged_slice["Input_Matched_ind"] = merged_slice.Rating_input_value1 == merged_slice.Rating_input_value2

            Factor_match_fiter = merged_slice.Factor_Matched_ind == False
            Input_mismatch_filter = merged_slice.Input_Matched_ind == False

            filter1 = Factor_match_fiter & Input_mismatch_filter
            policy_level_data1 = (
            merged_slice[filter1].loc[:, ['Rate_Table_Description', 'Peril_Name', 'Rating_Input_name1'
                                             , 'Rating_input_value1', 'Rating_input_value2']]).drop_duplicates()


            format_category = 'policy'
            slice_data = ("slices " + str(slice_no - 1) + ' VS ' + str(slice_no), " ", " ", " ")
            slice_header.append(slice_data)
            row_list , cap_list1 = format_output_data(policy_level_data1, format_category)
            if(len(row_list)==0):
                row_data = (" ", "No Differences", " ", " ")
                row_list.append(row_data)
            slice_header.extend(row_list)
            column_names = ('Slice Info', 'Rating variable', 'Slice X', 'Slice Y')
            slice_table = create_table(slice_header, column_names)
    else:
        slice_data = (" ", "No OOS Slices found...", " ", " ")
        slice_header.append(slice_data)
        slice_data = ("Slice Info", "Rating Variable", " ", " ")
        slice_table = pd.DataFrame(slice_header,columns=slice_data)


    print("successful completion" )
    return policy_table, addt_table, slice_table, cap_table
