from flask import Flask, render_template, request, after_this_request
from project_HO_prem_compare import Do_Compare_Home
from project_prem_compare import Do_Compare_Auto
import pandas as pd
import csv
import os

app = Flask(__name__)

def create_table(row_list,column_names):
    if len(row_list) >= 1:
        new_table = row_list
    else:
        row_data = (" ", "No Differences", " ", " ")
        row_list.append(row_data)
        new_table = row_list
    return pd.DataFrame(new_table,columns=column_names)

def crt_main_table(job1_data,job2_data, job2fname):
        main_list = []
        col_head = (' ', ' ', ' ')
        main_data = ("Product Name     ", str(job1_data.loc[1, "Product_Name"]), ' ')
        main_list.append(main_data)
        main_data = ("State            ", str(job1_data.loc[1, "Jurisdiction"]), ' ')
        main_list.append(main_data)
        main_data = ("Account Number  ", str(int(job1_data.loc[1, "Account_Number"])),' ')
        main_list.append(main_data)
        main_data = ("Policy Number    ", str(int(job1_data.loc[1, "Policy_Number"])),' ')
        main_list.append(main_data)
        main_data = ("Job Number 1     ",str(int(job1_data.loc[1, "Job_Number"])) , ' ')
        main_list.append(main_data)
        main_data = (' ', "Period start Date  ", str(job1_data.loc[1, "Policy_Term_Effective_Date"]))
        main_list.append(main_data)
        main_data = (' ', "  Eff Date  ", str(job1_data.loc[1, "Slice_Date"]))
        main_list.append(main_data)
        main_data = (' ', "   RateBook  ", str(job1_data.loc[1, "Ratebook_Edition"]))
        main_list.append(main_data)
        if job2fname not in ('', ' ', None):
            main_data = ("Job Number 2     ", str(int(job2_data.loc[1, "Job_Number"])), ' ')
            main_list.append(main_data)
            main_data = (' ', "Period start Date  ", str(job2_data.loc[1, "Policy_Term_Effective_Date"]))
            main_list.append(main_data)
            main_data = (' ', "  Eff Date  ",  str(job2_data.loc[1, "Slice_Date"]))
            main_list.append(main_data)
            main_data = (' ', "   RateBook  ",  str(job2_data.loc[1, "Ratebook_Edition"]))
            main_list.append(main_data)
        else:
            main_data = ("Job Number 2     ", "N/A",' ')
            main_list.append(main_data)
        main_table = create_table(main_list, col_head)
        return main_table

def read_pd(path_to_job):
    with open(path_to_job, 'r') as f:
        col_names = csv.reader(f)
        i = next(col_names)
        number_of_cols = len(i)
    cols_to_import = [i for i in range(0, number_of_cols)]
    job_data = pd.read_csv(path_to_job,usecols=cols_to_import)
    job_data.columns = job_data.columns.str.replace(' ', '_')
    return job_data

@app.route("/")
def home():
    #@after_this_request
    #def my_background_task2(response):
    #    folder = 'static/css/images/'
    #    for filename in os.listdir(folder):
    #        file_path = os.path.join(folder, filename)
    #        os.unlink(file_path)
    #    return response
    return render_template('Home.html')

@app.route("/result", methods=['POST'])
def about():
    try:
        @after_this_request
        def my_background_task1(response):
            folder = 'uploads/'
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                os.unlink(file_path)
            return response

        app.config['UPLOADED_CSV'] = 'uploads'
        stop = 0
        error1 = "To Extract the rating variables from worksheet, Please provide prior job' or To Compare the worksheets, " \
                 "Please provide both prior job and current job"
        error2 = "Worksheets are not of same LOBs. Please select worksheets of a policy from same LOB to compare"
        error3 = "Jobs selected are of different Policies. Please select worksheets of the same policy to compare"
        error4 = "Only CSV files (downloaded via ‘Generate Worksheet’ on PC quote screen) is supported"
        disc1 = "Note: Deceased Driver Stabilization Factor(DDSF) is not compared here..Please check with IT to know more on the DDSF on the policy"

        if request.method == 'POST':

            path_to_job1 = request.files.get('Worksheet1')
            path_to_job2 = request.files.get('Worksheet2')
            job1fname = request.files['Worksheet1'].filename
            job2fname = request.files['Worksheet2'].filename
            job1ext = str(job1fname).lower().endswith(('.csv'))
            job2ext = str(job2fname).lower().endswith(('.csv'))
            if (job1ext != True and job1fname not in ('', ' ', None)) or (
                    job2ext != True and job2fname not in ('', ' ', None)):
                out = error4
                stop = 1
            else:
                if (job1fname in ('', ' ', None) or job2fname in ('', ' ', None)):
                    if job1fname in ('', ' ', None) and job2fname in ('', ' ', None):
                        out = error1
                        stop = 1
                    else:
                        if job2fname in ('', ' ', None):
                            path_to_job1.save(os.path.join(app.config['UPLOADED_CSV'], job1fname))
                            path1 = os.path.join(app.config['UPLOADED_CSV'], job1fname)
                            job1_data = read_pd(path1)
                        else:
                            path_to_job2.save(os.path.join(app.config['UPLOADED_CSV'], job2fname))
                            path2 = os.path.join(app.config['UPLOADED_CSV'], job2fname)
                            job1_data = read_pd(path2)
                        job2fname = ' '
                        job2_data = ' '
                else:
                    path_to_job1.save(os.path.join(app.config['UPLOADED_CSV'], job1fname))
                    path_to_job2.save(os.path.join(app.config['UPLOADED_CSV'], job2fname))
                    path1 = os.path.join(app.config['UPLOADED_CSV'], job1fname)
                    path2 = os.path.join(app.config['UPLOADED_CSV'], job2fname)
                    job1_data = read_pd(path1)
                    job2_data = read_pd(path2)
                    if job1_data.loc[1, "Product_Name"] != job2_data.loc[1, "Product_Name"]:
                        out = error2
                        stop = 1
                    else:
                        if job1_data.loc[1, "Policy_Number"] != job2_data.loc[1, "Policy_Number"]:
                            out = error3
                        # stop = 1
                if stop != 1:
                    #col_names = job1_data.columns.tolist()
                    if job2fname not in ('', ' ', None):
                        print('Processing....' + str(job1_data.loc[1, "Job_Number"]) + " & " + str(job2_data.loc[1, "Job_Number"]))
                    else:
                        print('Processing....' + str(job1_data.loc[1, "Job_Number"]))
                    if job1_data.loc[1, "Product_Name"] == 'Personal Auto':
                        driver_table, policy_table, vehicle_table, misc_table, cap_table = Do_Compare_Auto(job1_data, job2_data,
                                                                                                job2fname)
                        main_table = crt_main_table(job1_data, job2_data, job2fname)
                    else:
                        policy_table, addt_table, slice_table, cap_table = Do_Compare_Home(job1_data, job2_data, job2fname
                                                                                )
                        main_table = crt_main_table(job1_data, job2_data, job2fname)
        if stop == 1:
            return render_template("About.html", tables=[out], titles=' ')
        else:
            # images = os.listdir('static/css/images/')
            if job1_data.loc[1, "Product_Name"] != 'Personal Auto':
                return render_template("About.html", tables=[
                    main_table.to_html(classes='data', index=False, justify='left', header=False),
                    policy_table.to_html(classes='data', index=False, justify='left'),
                    cap_table.to_html(classes='data', index=False, justify='left'),
                    addt_table.to_html(classes='data', index=False, justify='left'),
                    slice_table.to_html(classes='data', index=False, justify='left')])

            else:
                return render_template("About.html", tables=[
                    main_table.to_html(classes='data', index=False, justify='left', header=False),
                    driver_table.to_html(classes='data', index=False, justify='left'),
                    policy_table.to_html(classes='data', index=False, justify='left'),
                    vehicle_table.to_html(classes='data', index=False, justify='left'),
                    cap_table.to_html(classes='data', index=False, justify='left'),
                    misc_table.to_html(classes='data', index=False, justify='left'),
                    disc1
                ])
    except Exception as err:
        if (request.environ.get('HTTP_X_REAL_IP', request.remote_addr)) != '10.184.6.186':
            return render_template("About.html",tables=["Worksheet compare failed :( .... Please send the worksheets to fix the cause of failure... "], titles=' ')
        else:
            return render_template("About.html", tables=[err], titles=' ')


if __name__ == "__main__":
    app.run(debug=False)


