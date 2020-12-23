import pandas as pd
from matplotlib import pyplot as plt

def create_plot(cap_list):
    if len(cap_list) > 0:
        column_names = (' ', 'Peril', 'Job1', ' Job2')
        Cap_df = pd.DataFrame(cap_list, columns=column_names)
        Cap_df.index = Cap_df.Peril
        plt.tight_layout()
        Cap_df.drop(["Peril"], axis=1, inplace=True)
        ax = Cap_df.plot(kind="barh", stacked=False)
        for p in ax.patches:
            ax.annotate("%.2f" % p.get_width(), (p.get_x() + p.get_width(), p.get_y()), xytext=(5, 10),
                        textcoords='offset points')
        plt.savefig('static/css/images/' + 'capped.png',  bboxinches ='tight')

def ho_read_n_format(data,col_names):
    cvg_rat_vars = (
        'limit', 'limit_code', 'credit_tier', 'credit_model', 'points', 'deductible', 'coverage_term', 'cov_exists',
        'coverage_option')
    limit_vars = ('Coverage - B', 'Coverage - C', 'Coverage - D', 'Coverage - E', 'Access Coverage - Limited Water',
                  'Additional Living Expense Term',
                  'Coverage - C excluding the availability check', 'Matching Coverage', 'Building Ordinance or Law'
                  )
    peril_vars = ('uw_tier', 'credit score', 'experience_points')
    key_words = (
        'coverage_code', 'cov_subtype', 'age_group', 'rating_component', 'rating_component', 'coverage', 'variable')

    if "Input_Name_7" in col_names:
        no_of_input_cols = 7
    else:
        if "Input_Name_6" in col_names:
            no_of_input_cols = 6
        else:
            if "Input_Name_5" in col_names:
                no_of_input_cols = 5
            else:
                if "Input_Name_4" in col_names:
                    no_of_input_cols = 4
                else:
                    if "Input_Name_3" in col_names:
                        no_of_input_cols = 3

    job_num = int(data.loc[1, "Job_Number"])
    eff_date = data.loc[1,"Slice_Date"]

    row_num = 0
    row_list = []
    col_name = 'Rating_input_value1'
    column_names = (
        'Rate_Table_Description', 'Peril_Name', 'Policy', 'Coverage_Pattern_Code', 'Rating_Input_name1', col_name,
        'Factor_Value_1', 'Input_type', 'orig_row_number', 'Slices')
    slice_peril_name = ' '
    end_slice = 0
    slice_num = 0

    base_prem = 0
    base_cap_prem_count = 0
    uncap_prem_count = 0
    cap_prem_count = 0
    BP = 0
    UP = 0
    RCF = 1.00
    CP = 0

    col1_prefix = 'Input_Name_'
    col2_prefix = 'Input_Value_'
    for idx, row in data.iterrows():
        row_num = row_num + 1

        if (row['Record_Type'] == 'TableLookup'
                and row['Scenario_Code'] == 'HOStandardPass'
                and (row['Factor_Name_1'] == 'factor'
                     or row['Factor_Name_1'] == 'rate')
                and row['Input_Name_1'] != 'bi_limit'
                and row['Rate_Table_Description'] != "UW Tier"
                and row['Rate_Table_Description'] != 'Rating dependencies'
        ):
            if slice_peril_name == ' ':
                slice_peril_name = row['Peril_Name']
            if slice_peril_name == row['Peril_Name']:
                if slice_num == 0:
                    slice_num = 1
                else:
                    if end_slice == row_num - 1:
                        slice_num = slice_num
                    else:
                        slice_num = slice_num + 1
                end_slice = row_num

            for j in range(no_of_input_cols):
                col_suffix = str(j + 1)
                input_col1 = col1_prefix + col_suffix
                input_col2 = col2_prefix + col_suffix
                # j = i+1
                Rate_table_desc = row['Rate_Table_Description']
                Rating_peril_name = row['Peril_Name']
                coverage = row['Coverage_Pattern_Code']
                if row[input_col1] in cvg_rat_vars:
                    input_name = row['Rate_Table_Description'] + " " + row[input_col1]
                else:
                    if row[input_col1] in peril_vars:
                        input_name = row['Peril_Name'] + " " + row[input_col1]
                    else:
                        if row[input_col1] in ('applies', 'discount_applies', 'discount_type'):
                            input_name = row['Rate_Table_Description']
                        else:
                            input_name = row[input_col1]

                input_value = row[input_col2]
                factor = row['Factor_Value_1']

                if input_name == 'additional_prem_type':
                    input_value = input_name

                if (input_value.__str__() != 'nan'
                        and factor != '0'
                        and input_name not in key_words):
                    row_data = (Rate_table_desc, Rating_peril_name, ' ',
                                coverage, input_name, input_value, factor, ' ', ' ', slice_num)
                    row_list.append(row_data)

                input_value = ' '
                input_name = ' '

        if row['Record_Type'] == 'RateCapFactor':
            input_name = "Rate Cap Factor"
            input_value = row['Factor_Value_1']
            Rate_table_desc = row['Rate_Table_Description']
            Rating_peril_name = ' '
            coverage = row['Coverage_Pattern_Code']
            factor = row['Factor_Value_1']
            addl_slc_num = 1
            RCF = factor
            if (input_value.__str__() != 'nan'
            and factor != '0'
            and input_name not in key_words):
                row_data = (
                Rate_table_desc, Rating_peril_name, ' ', coverage, input_name, input_value, factor, ' ', ' ', addl_slc_num)
                row_list.append(row_data)

        if row['Record_Type'] == 'Base Premium (P1)':
            input_name = row['Record_Type'] + row['Peril_Name']
            input_value = row['Premium_Amount']
            Rate_table_desc = row['Rate_Table_Description']
            coverage = ' '
            Rating_peril_name = row['Peril_Name']
            factor = row['Premium_Amount']
            base_prem = base_prem + factor
            base_cap_prem_count = base_cap_prem_count  + 1
            addl_slc_num = 1
            if (input_value.__str__() != 'nan'
            and factor != '0'
            and input_name not in key_words):
                row_data = (
                Rate_table_desc, Rating_peril_name, ' ', coverage, input_name, input_value, factor, ' ', ' ', addl_slc_num)
                row_list.append(row_data)
        else:
            if base_cap_prem_count  > 1:
                input_name = 'Base Premium'
                input_value = base_prem
                Rate_table_desc = 'Base Premium'
                coverage = ' '
                Rating_peril_name = ' '
                factor = base_prem
                BP = factor
                row_data = (
                    Rate_table_desc, Rating_peril_name, ' ', coverage, input_name, input_value, factor, ' ', ' ',
                    addl_slc_num)
                row_list.append(row_data)
                base_prem = 0
                base_cap_prem_count = 0

        if row['Record_Type'] == 'Uncapped Premium (P2)':
            input_name = row['Record_Type'] + row['Peril_Name']
            input_value = row['Premium_Amount']
            Rate_table_desc = row['Rate_Table_Description']
            coverage = ' '
            Rating_peril_name = row['Peril_Name']
            factor = row['Premium_Amount']
            base_prem = base_prem + factor
            uncap_prem_count = uncap_prem_count + 1
            addl_slc_num = 1
            if (input_value.__str__() != 'nan'
            and factor != '0'
            and input_name not in key_words):
                row_data = (
                Rate_table_desc, Rating_peril_name, ' ', coverage, input_name, input_value, factor, ' ', ' ', addl_slc_num)
                row_list.append(row_data)
        else:
            if uncap_prem_count > 1:
                input_name = 'Uncap Premium'
                input_value = base_prem
                Rate_table_desc = 'Uncap Premium'
                coverage = ' '
                Rating_peril_name = ' '
                factor = base_prem
                UP = factor
                row_data = (
                    Rate_table_desc, Rating_peril_name, ' ', coverage, input_name, input_value, factor, ' ', ' ',
                    addl_slc_num)
                row_list.append(row_data)
                base_prem = 0
                uncap_prem_count = 0

        if row['Record_Type'] == 'Capped':
            input_name = "Capped Premium for " + row['Peril_Name']
            input_value = row['Premium_Amount']
            Rate_table_desc = row['Rate_Table_Description']
            coverage = ' '
            Rating_peril_name = row['Peril_Name']
            factor = row['Premium_Amount']
            base_prem = base_prem + factor
            cap_prem_count = cap_prem_count + 1
            addl_slc_num = 1
            if (input_value.__str__() != 'nan'
                and factor != '0'
                and input_name not in key_words):
                row_data = (
                    Rate_table_desc, Rating_peril_name, ' ', coverage, input_name, input_value, factor, ' ',
                            ' ', addl_slc_num)
                row_list.append(row_data)
        else:
            if cap_prem_count > 1:
                input_name = 'Capped Premium'
                input_value = base_prem
                Rate_table_desc = 'Capped Premium'
                coverage = ' '
                Rating_peril_name = ' '
                factor = base_prem
                CP = factor
                row_data = (
                    Rate_table_desc, Rating_peril_name, ' ', coverage, input_name, input_value, factor, ' ',
                            ' ',
                            addl_slc_num)
                row_list.append(row_data)


                ###################Capping %age###

                if BP > 0 and UP > 0:
                    if UP > BP:
                        cap_percentage = round(((float(RCF) * (float(UP) / float(BP))) - 1) * 100, 1)
                    else:
                        cap_percentage = round(((float(RCF) * (float(UP) / float(BP))) - 1) * 100, 1)
                    input_name = 'Cap Percentage'
                    input_value = str(cap_percentage) + str("%")
                    Rate_table_desc = 'Cap Percentage'
                    Rating_peril_name = ' '
                    coverage = ' '
                    factor = cap_percentage
                    row_data = (
                        Rate_table_desc, Rating_peril_name, ' ', coverage, input_name, input_value, factor, ' ', ' ',
                        addl_slc_num)
                    row_list.append(row_data)

                    #################Capping type#################
                    if UP < BP and float(RCF) > 1 and cap_percentage > 0:
                        capping_type = "Floor"
                    else:
                        capping_type = "Ceiling"
                    input_name = 'Capping type'
                    input_value = capping_type
                    Rate_table_desc = 'Capping type'
                    Rating_peril_name = ' '
                    coverage = ' '
                    factor = capping_type
                    row_data = (
                        Rate_table_desc, Rating_peril_name, ' ', coverage, input_name, input_value, factor, ' ', ' ',
                        addl_slc_num)
                    row_list.append(row_data)
                    base_prem = 0
                    cap_prem_count = 0

    Policy_input_test = pd.DataFrame(columns=column_names)
    Policy_input_test = Policy_input_test.append(pd.DataFrame(row_list, columns=column_names))
    return Policy_input_test, slice_num, job_num, eff_date


def format_output_data(data, format_category):
    Veh_rat_vars = ('vehicle_type', '_density_code', 'limit_greater_100_300', 'vehicle_use', 'vehicle_history_indicator'
                                                                                             'leased', 'luxury_vehicle',
                    'full_coverage', 'auto_type', 'Model_Year', 'vehicle_type', 'vehicle_category_code', 'limit_code',
                    'model_group', 'zip_code',
                    'PABICov_Ext fas_symbol', 'PAMedical_Ext fas_symbol', 'PAPDCov_Ext fas_symbol',
                    'PAUIMBICov fas_symbol', 'PAUMBI_Ext fas_symbol', 'PACollisionCov fas_symbol',
                    'PAComprehensiveCov fas_symbol'
                    )

    cvg_rat_vars = ('limit_code', 'credit_tier', 'credit_model', 'points', 'fas_symbol')
    key_words = (
        'coverage_code', 'cov_subtype', 'age_group', 'rating_component', 'rating_componenet', 'coverage', 'variable')
    cap_info = ('Capped', 'Base Premium', 'Uncap Premium', 'Uncapped Premium (P2)', 'Base Premium (P1)',
                'Cap Percentage', 'Capping type', 'Rate Cap Factor', 'Capped Premium')
    category_list = []
    row_list = []
    cap_list = []
    for i in range(len(data)):

        if format_category == 'policy':
            if i == 0:
                str1 = data.iloc[i, 1]
                category_list.append(str1)
                row_data = ("Data and Factor Difference", " ", " ", " ")
                row_list.append(row_data)

            if ((data.iloc[i, 2] not in category_list) & (data.iloc[i, 2] not in key_words) &
                (((data.iloc[i, 2] in cap_info) or (data.iloc[i, 0] in cap_info)) or
                    (data.iloc[i, 2] not in Veh_rat_vars))):
                if ((data.iloc[i, 2] in cap_info) or (data.iloc[i, 0] in cap_info)):
                    if data.iloc[i, 2] != pd.isnull:
                        str1 = data.iloc[i, 2]
                        category_list.append(str1)
                        if data.iloc[i, 2].__str__() == 'nan':
                            data.iloc[i, 2] = ' '
                        if data.iloc[i, 3].__str__() == 'nan':
                            data.iloc[i, 3] = ' '
                        if data.iloc[i, 4].__str__() == 'nan':
                            data.iloc[i, 4] = ' '
                        row_data = (" ", data.iloc[i, 2], data.iloc[i, 3], data.iloc[i, 4])
                        cap_list.append(row_data)
                else:
                    if data.iloc[i, 2] != pd.isnull:
                        str1 = data.iloc[i, 2]
                        category_list.append(str1)
                        if data.iloc[i, 2].__str__() == 'nan':
                            data.iloc[i, 2] = ' '
                        if data.iloc[i, 3].__str__() == 'nan':
                            data.iloc[i, 3] = ' '
                        if data.iloc[i, 4].__str__() == 'nan':
                            data.iloc[i, 4] = ' '
                        row_data = (" ", data.iloc[i, 2], data.iloc[i, 3], data.iloc[i, 4])
                        row_list.append(row_data)

            #if data.iloc[i, 0] == 'Capped':
                #cap_data = (data.iloc[i,1], data.iloc[i, 2], data.iloc[i, 3], data.iloc[i, 4])
                #cap_list.append(cap_data)

    #create_plot(cap_list)

    return row_list, cap_list
