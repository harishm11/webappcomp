import pandas as pd
from matplotlib import pyplot as plt



def map_cov(coverage):
    cov_dict = {
        "Accident Forgiveness": "PAAccidentForgiveness_Ext",
        "Accidental Death Benefits": "PAAccDeathBenefitsCov_Ext",
        "Accidental Death Benefits on DOC": "PAAccDeathBftDOCCov_Ext",
        "Bodily Injury": "PABICov_Ext",
        "Drive Other Car BI": "PADOCBI_Ext",
        "Drive Other Car PD": "PADOCPD_Ext",
        "Extraordinary Medical Benefits": "ExtraOrdMedBftCov_Ext",
        "Extraordinary Medical Benefits on DOC": "ExtraOrdMedBftDOCCov_Ext",
        "First Party Benefits Combination Package": "FPBftCombPackCov_Ext",
        "First Party Benefits Package on DOC": "FPBftPackDOCCov_Ext",
        "Funeral Expense Benefits": "FuneralExpenseBftCov_Ext",
        "Funeral Expense Benefits on DOC": "FuneralExpBftDOCCov_Ext",
        "Income Loss Benefits": "IncomeLossBftCov_Ext",
        "Income Loss Benefits on DOC": "IncomeLossBftDOCCov_Ext",
        "Limited Tort": "LimitedTortCov_Ext",
        "Medical": "PAMedicalPA_Ext",
        "Property Damage": "PAPDCov_Ext",
        "Underinsured Motorist - Bodily Injury": "PAUIMBICovPA_Ext",
        "Uninsured Motorist - Bodily Injury": "PAUMBIPACov_Ext",
        "Collision": "PACollisionCov",
        "Collision Plus/Loss of Use": "PACollLossOfUseCov_Ext",
        "Comprehensive": "PAComprehensiveCov",
        "Contents - Fire Coverage": "PAContentFireCov_Ext",
        "Customization": "PACustomCov_Ext",
        "Glass Deductible Buyback": "GlassDedBuybackCov_Ext",
        "New Car Replacement": "PANewCarReplCov_Ext",
        "Original Equipment Manufacturer (OEM)": "PAOEMCov_Ext",
        "Rental Reimbursement Coverage": "PARentalCov",
        "Residual Debt Coverage": "PADebtCov_Ext",
        "Rideshare Coverage": "PARideshare_Ext",
        "Towing and Road Service": "PATowingLaborCov",
        "Auto Death Ind & Specific Disability": "PADeathDisabilityCov",
        "Medical": "PAMedical_Ext",
        "Underinsured Motorist - Bodily Injury": "PAUIMBICov",
        "Uninsured Motorist - Bodily Injury": "PAUMBI_Ext",
        "Safety Glass - Waiver of Deductible": "PASafeGlassWaiver_Ext"
    }
    coverage = str([key for key, value in cov_dict.items() if value == coverage]).strip('[]')
    return coverage


def create_graph(cap_list,format_category ):

    if format_category == 'vehicle':
        if len(cap_list) > 0:
            vin = [x[0] for x in cap_list]
            vehs = []
            [vehs.append(x) for x in vin if x not in vehs]
            for veh in vehs:
                column_names = ('VIN','Coverage','Job1', ' Job2')
                Cap_df = pd.DataFrame(cap_list, columns=column_names)
                Cap_df.index = Cap_df.Coverage
                plt.tight_layout()
                Cap_df.drop(["Coverage"], axis=1, inplace=True)
                ax=Cap_df.plot(kind="barh", stacked=False)
                for p in ax.patches:
                    ax.annotate("%.2f" % p.get_width(), (p.get_x() + p.get_width(), p.get_y()), xytext=(5, 10), textcoords='offset points')
                plt.savefig('static/css/images/' + veh + '.png', bboxinches ='tight')

def read_n_format(data,col_names):
    cvg_rat_vars = ('limit_code', 'credit_tier', 'credit_model', 'points', 'fas_symbol', 'Base Rate')
    key_words = ('cov_subtype', 'age_group', 'Cov_subtype', 'coverage_code')


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

    column_names = ('Rate_Table_Description', 'Driver_Name', 'VIN', 'Coverage_Pattern_Code', 'Rating_Input_name1',
                    'Rating_input_value1', 'Factor_Value_1'
                    , 'Input_type', 'orig_row_number')
    row_list = []
    col1_prefix = 'Input_Name_'
    col2_prefix = 'Input_Value_'

    cap_vin = ' '
    base_prem = 0
    cap_prem =0
    uncap_prem = 0
    base_cap_prem_count = 0
    uncap_prem_count = 0
    cap_prem_count = 0
    BP = 0
    UP = 0
    RCF= 1.00
    CP= 0

    for idx, row in data.iterrows():
        coverage = row['Coverage_Pattern_Code']
        coverage = map_cov(coverage)
        if row['Record_Type'] == 'TableLookup' and (row['Factor_Name_1'] == 'factor' or row['Factor_Name_1'] == 'rate'):

            Rate_table_desc = row['Rate_Table_Description']
            Drv_Name = row['Driver_Name']
            Vin = row['VIN']



            if (row['Scenario_Code'] == 'PAStandardPass'):

                Rate_table_desc = row['Rate_Table_Description']
                Drv_Name = row['Driver_Name']
                Vin = row['VIN']


                factor = row['Factor_Value_1']


                for j in range(no_of_input_cols):
                    col_suffix = str(j + 1)
                    input_col1 = col1_prefix + col_suffix
                    input_col2 = col2_prefix + col_suffix

                    if row[input_col1] in cvg_rat_vars:

                        input_name = coverage + " " + row[input_col1]
                        input_value = row[input_col2]
                    else:
                        if row[input_col1] in ('if_applies', 'applies', 'discount_applies', 'discount_type'):
                            if row[input_col1] == 'coverage_code':

                                input_name = row['Rate_Table_Description'] + " " + coverage
                                Rate_table_desc = row['Rate_Table_Description'] + " for " + coverage
                            else:
                                input_name = row['Rate_Table_Description']
                        else:
                            input_name = row[input_col1]

                    input_value = row[input_col2]

                    if row['Rate_Table_Description'] == 'Base rate':
                        if (row[input_col1] == 'coverage_code'):

                            input_name = row['Rate_Table_Description'] + " for " + coverage
                            input_value = row['Factor_Value_1']

                    if (input_name.__str__() != 'nan'
                            and factor != '0'
                            and input_name not in key_words):
                        row_data = (Rate_table_desc, Drv_Name, Vin,
                                    coverage, input_name, input_value, factor, ' ', ' ')
                        row_list.append(row_data)

                    input_value = ' '
                    input_name = ' '

        input_value = ' '
        input_name = ' '
        #print(row_list)
        if row['Record_Type'] == 'AverageDriverClassFactor':
            Rate_table_desc = coverage + " " + "ADCF "
            Drv_Name = row['Driver_Name']
            Vin = row['VIN']
            input_name = coverage + " " + "ADCF "
            input_value = row['Factor_Value_1']
            factor = row['Factor_Value_1']
            if (input_value.__str__() != 'nan'
                    and factor != '0'
                    and input_name not in key_words):
                row_data = (Rate_table_desc, Drv_Name, Vin,
                            coverage, input_name, input_value, factor, ' ', ' ')
                row_list.append(row_data)

        if row['Record_Type'] == 'RateCapFactor':
            input_name = "Rate Cap Factor"
            input_value = row['Factor_Value_1']
            Rate_table_desc = row['Rate_Table_Description']
            Drv_Name = row['Driver_Name']
            Vin = row['VIN']
            factor = row['Factor_Value_1']
            RCF = factor
            if (input_value.__str__() != 'nan'
                    and factor != '0'
                    and input_name not in key_words):
                row_data = (Rate_table_desc, Drv_Name, Vin,
                            coverage, input_name, input_value, factor, ' ', ' ')
                row_list.append(row_data)

        if row['Record_Type'] == 'Capped':
            input_name = "Capped Premium for " + coverage
            input_value = row['PremiumAmount']
            Rate_table_desc = row['Rate_Table_Description']
            Drv_Name = row['Driver_Name']
            Vin = row['VIN']
            factor = row['PremiumAmount']
            if cap_vin == ' ':
                cap_vin = Vin
                if cap_vin == Vin:
                    cap_prem = cap_prem + factor
                    cap_prem_count = cap_prem_count + 1
            else:

                    cap_prem = cap_prem + factor
                    cap_prem_count = cap_prem_count + 1
            if (input_value.__str__() != 'nan'
                    and factor != '0'
                    and input_name not in key_words):
                row_data = (Rate_table_desc, Drv_Name, Vin,
                            coverage, input_name, input_value, factor, ' ', ' ')
                row_list.append(row_data)
        else:
            if cap_prem_count > 1:
                input_name = 'Capped Premium'
                input_value = cap_prem
                Rate_table_desc = 'Capped Premium'
                Drv_Name = ' '
                Vin = cap_vin
                coverage = ' '
                factor = cap_prem
                CP = factor
                row_data = (Rate_table_desc, Drv_Name, Vin,
                            coverage, input_name, input_value, factor, ' ', ' ')
                row_list.append(row_data)
                cap_vin = ' '
                cap_prem = 0
                cap_prem_count = 0

                coverage = row['Coverage_Pattern_Code']
                coverage = map_cov(coverage)

        if row['Record_Type'] == 'Base Premium (P1)':
            input_name = row['Record_Type'] + ' for ' + coverage
            input_value = row['PremiumAmount']
            Rate_table_desc = row['Rate_Table_Description']
            Drv_Name = row['Driver_Name']
            Vin = row['VIN']
            factor = row['PremiumAmount']
            if cap_vin == ' ':
                cap_vin = Vin
                if cap_vin == Vin:
                    base_prem = base_prem + factor
                    base_cap_prem_count = base_cap_prem_count + 1
            else:

                    base_prem = base_prem + factor
                    base_cap_prem_count = base_cap_prem_count + 1
            if (input_value.__str__() != 'nan'
                    and factor != '0'
                    and input_name not in key_words):
                row_data = (Rate_table_desc, Drv_Name, Vin,
                            coverage, input_name, input_value, factor, ' ', ' ')
                row_list.append(row_data)

        else:
            if base_cap_prem_count > 1:
                input_name = 'Base Premium'
                input_value = base_prem
                Rate_table_desc = 'Base Premium'
                Drv_Name = ' '
                Vin = cap_vin
                coverage = ' '
                factor = base_prem
                BP = factor
                row_data = (Rate_table_desc, Drv_Name, Vin,
                            coverage, input_name, input_value, factor, ' ', ' ')
                row_list.append(row_data)
                cap_vin = ' '
                base_prem = 0
                base_cap_prem_count = 0

                coverage = row['Coverage_Pattern_Code']
                coverage = map_cov(coverage)

        if row['Record_Type'] == 'Uncapped Premium (P2)':
            input_name = row['Record_Type'] + ' for ' + coverage
            input_value = row['PremiumAmount']
            Rate_table_desc = row['Rate_Table_Description']
            Drv_Name = row['Driver_Name']
            Vin = row['VIN']
            factor = row['PremiumAmount']
            if cap_vin == ' ':
                cap_vin = Vin
                if cap_vin == Vin:
                    uncap_prem = uncap_prem + factor
                    uncap_prem_count = uncap_prem_count + 1
            else:

                    uncap_prem = uncap_prem + factor
                    uncap_prem_count = uncap_prem_count + 1
            if (input_value.__str__() != 'nan'
                    and factor != '0'
                    and input_name not in key_words):
                row_data = (Rate_table_desc, Drv_Name, Vin,
                            coverage, input_name, input_value, factor, ' ', ' ')
                row_list.append(row_data)

        else:
            if uncap_prem_count > 1:
                input_name = 'Uncap Premium'
                input_value = uncap_prem
                Rate_table_desc = 'Uncap Premium'
                Drv_Name = ' '
                Vin =  cap_vin
                coverage = ' '
                factor = uncap_prem
                UP = factor
                row_data = (Rate_table_desc, Drv_Name, Vin,
                            coverage, input_name, input_value, factor, ' ', ' ')
                row_list.append(row_data)

                #################Capping percentage#################
                if BP > 0 and UP > 0:
                    if UP > BP:
                        cap_percentage = round(((float(RCF) * (float(UP) / float(BP))) - 1) * 100, 1)
                    else:
                        cap_percentage = round(((float(RCF) * (float(UP) / float(BP))) - 1) * 100, 1)
                    input_name = 'Cap Percentage'
                    input_value = str(cap_percentage) + str("%")
                    Rate_table_desc = 'Cap Percentage'
                    Drv_Name = ' '
                    Vin = cap_vin
                    coverage = ' '
                    factor = cap_percentage
                    row_data = (Rate_table_desc, Drv_Name, Vin,
                                coverage, input_name, input_value, factor, ' ', ' ')
                    row_list.append(row_data)

                    #################Capping type#################
                    if UP < BP and float(RCF) > 1 and cap_percentage > 0:
                        capping_type = "Floor"
                    else:
                        capping_type = "Ceiling"
                    input_name = 'Capping type'
                    input_value = capping_type
                    Rate_table_desc = 'Capping type'
                    Drv_Name = ' '
                    Vin = cap_vin
                    coverage = ' '
                    factor = capping_type
                    row_data = (Rate_table_desc, Drv_Name, Vin,
                                coverage, input_name, input_value, factor, ' ', ' ')
                    row_list.append(row_data)

                    cap_vin = ' '
                    base_prem = 0
                    uncap_prem_count = 0
                    coverage = row['Coverage_Pattern_Code']
                    coverage = map_cov(coverage)

    Policy_input_test = pd.DataFrame(columns=column_names)
    Policy_input_test = Policy_input_test.append(pd.DataFrame(row_list, columns=column_names))
    return Policy_input_test, job_num, eff_date;


def format_output_data(data, format_category, job2fname):
    cap_list = []
    Veh_rat_vars = ('vehicle_type', '_density_code', 'limit_greater_100_300', 'vehicle_use', 'vehicle_history_indicator'
                                                                                             'leased', 'luxury_vehicle',
                    'full_coverage', 'auto_type', 'Model_Year', 'vehicle_type', 'vehicle_category_code', 'limit_code',
                    'model_group', 'zip_code','fas_symbol' , 'Base Rate',
                    'FAS Factor')

    key_words = ('coverage_code', 'cov_subtype', 'age_group')
    cap_info = ('Capped','Base Premium','Uncap Premium','Uncapped Premium (P2)','Base Premium (P1)',
                    'Cap Percentage','Capping type','Rate Cap Factor','Capped Premium')
    category_list = []
    row_list = []
    cap_list = []
    for i in range(len(data)):
        if format_category == 'driver':
            if data.iloc[i, 1] not in category_list :
                category_list = []
                str1 = data.iloc[i, 1]
                category_list.append(str1)
                if data.iloc[i, 1].__str__() != ' ':
                    row_data = (data.iloc[i, 1], " ", " ", " ")
                    row_list.append(row_data)

            if ((data.iloc[i, 2] not in category_list) & (data.iloc[i, 2] not in key_words) and
                (data.iloc[i, 2] not in cap_info) & (data.iloc[i, 0] not in cap_info)
            and (data.iloc[i, 2] not in Veh_rat_vars)):
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

        if format_category == 'policy':
            if i == 0:
                str1 = data.iloc[i, 1]
                category_list.append(str1)


            if ((data.iloc[i, 2] not in category_list) & (data.iloc[i, 2] not in key_words) &
                    (data.iloc[i, 2] not in cap_info) & (data.iloc[i, 0] not in cap_info) and
                    (data.iloc[i, 2] not in Veh_rat_vars) & (data.iloc[i, 0] not in Veh_rat_vars)):
                if data.iloc[i, 2] != pd.isnull and (data.iloc[i, 3].__str__() != 'nan' and data.iloc[i, 4].__str__() != 'nan') \
                    or job2fname in ('', ' ', None):

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
                    #print(data.iloc[i, 3].__str__() )

        if format_category == 'vehicle':
            if data.iloc[i, 1] not in category_list and data.iloc[i, 1].__str__() != 'nan':
                category_list = []
                str1 = data.iloc[i, 1]
                category_list.append(str1)

                row_data =  ("VIN: " + str(data.iloc[i,1]) ," " , " " , " " )
                row_list.append(row_data)
                cap_list.append(row_data)

            if ((data.iloc[i, 2] not in category_list) and (data.iloc[i, 2] not in key_words) and
                    (((data.iloc[i, 2] in cap_info) or (data.iloc[i, 0] in cap_info)) or
                    ((data.iloc[i, 2] in Veh_rat_vars) or (data.iloc[i, 0] in Veh_rat_vars)))):
                if data.iloc[i, 2] != pd.isnull:
                    #print(data.iloc[i, 2])
                    if ((data.iloc[i, 2] in Veh_rat_vars) or (data.iloc[i, 0] in Veh_rat_vars)):
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
                    else:
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


            if data.iloc[i, 0] == 'Base Rate':
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

    #create_graph(cap_list,format_category )


    return row_list, cap_list

