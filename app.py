from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
mysql = MySQL(app)

app.secret_key = 'hospital'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'hospital'

def db():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    return cur

@app.route('/')
def home():
    return render_template('index.html')

#   Patient login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'pat_id' in request.form and 'pat_name' in request.form:
        pat_id = request.form['pat_id']
        pat_name = request.form['pat_name']
        cur = db()
        cur.execute("SELECT * FROM patient WHERE id = %s AND patient_name = %s",(pat_id,pat_name))
        pat_data = cur.fetchone()
        if pat_data:
            session['patlogged_in'] = True
            session['pat_id'] = pat_data['id']
            alerts = "Welcome Back"
            return redirect(url_for('dashboard',alerts=alerts))
        else:
            alertd = "Login details are incorrect. Please check it agaian."
            return render_template('login.html', alertd = alertd)
    if request.args.get('alertd'):
        alertd = request.args.get('alertd')
        return render_template('login.html', alertd = alertd)
    return render_template('login.html')

#   Patient Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if session.get('patlogged_in'):
        if request.args.get('alerts'):
            alerts = request.args.get('alerts')
            return render_template('patient/dashboard.html',alerts = alerts)
        return render_template('patient/dashboard.html')
    else:
        alertd = "Please login to continue."
        return redirect(url_for('login',alertd=alertd))

#   Patient Doctors List
@app.route('/pdoctlist', methods=['GET', 'POST'])
def pdoctlist():
    if session.get('patlogged_in'):
        cur = db()
        cur.execute("SELECT * FROM doctor")
        all_doct = cur.fetchall()
        return render_template('patient/doctorlist.html', all_doct = all_doct)
    else:
        alertd = "Please login to continue."
        return redirect(url_for('login',alertd=alertd))

#   Patient Medicines List
@app.route('/pmedlist', methods=['GET', 'POST'])
def pmedlist():
    if session.get('patlogged_in'):
        cur = db()
        cur.execute("SELECT * FROM medicine")
        all_med = cur.fetchall()
        return render_template('patient/medicinelist.html', all_med = all_med)
    else:
        alertd = "Please login to continue."
        return redirect(url_for('login',alertd=alertd))


#   Admin login 
@app.route('/adlogin', methods=['GET', 'POST'])
def adlogin():
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cur = db()
        cur.execute("SELECT * FROM admin WHERE email = %s AND password = %s ",(email,password))
        admin_data = cur.fetchone()
        if admin_data:
            session['adlogged_in'] = True
            session['admin_id'] = admin_data['id']
            alerts = "Welcome Back, Admin"
            return redirect(url_for('adashboard',alerts=alerts))
        else:
            alertd = "Login details are incorrect. Please try again"
            return render_template('admin/index.html',alertd = alertd)
    return render_template('admin/index.html')

#   Admin dashboard
@app.route('/adashboard')
def adashboard():
    if session.get('adlogged_in'):
        if request.args.get('alerts'):
            alerts = request.args['alerts']
            return render_template('admin/dashboard.html', alerts = alerts)
        else:
            return render_template('admin/dashboard.html')
    else:
        return redirect(url_for('adlogin'))

#   Admin Create Department
@app.route('/acreatedept', methods=['GET', 'POST'])
def acreatedept():
    if session.get('adlogged_in'):
        if request.method == 'POST' and 'dept' in request.form:
            dept = request.form['dept']
            print(dept)
            cur = db()
            cur.execute("SELECT * FROM department WHERE department_name = %s",(dept,))
            dept_data = cur.fetchone()
            if dept_data:
                alertd = "This department already exists. Try with another one."
                return render_template('admin/createdepartment.html', alertd = alertd)
            else:
                cur.execute("INSERT INTO department(department_name) VALUES(%s)",(dept,))
                mysql.connection.commit()
                alerts = "Depratment has been created successfully."
                return redirect(url_for('adashboard',alerts=alerts))
        return render_template('admin/createdepartment.html')
    else:
        return redirect(url_for('adlogin'))

#   Admin Create Doctor
@app.route('/acreatedoct', methods=['GET', 'POST'])
def acreatedoct():
    if session.get('adlogged_in'):
        cur = db()
        cur.execute("SELECT * FROM department")
        all_dept = cur.fetchall()
        if request.method == 'POST' and 'doct' in request.form and 'dept_id' in request.form:
            doct = request.form['doct']
            dept_id = request.form['dept_id']
            cur.execute("INSERT INTO doctor(doctor_name, department_id) VALUES(%s, %s)",(doct,dept_id))
            mysql.connection.commit()
            alerts = "Doctor record has been created successfully."
            return redirect(url_for('adashboard',alerts=alerts))
        return render_template('admin/createdoctor.html', all_dept = all_dept)
    else:
        return redirect(url_for('adlogin'))

#   Admin Create Patient
@app.route('/acreatepat', methods=['GET', 'POST'])
def acreatepat():
    if session.get('adlogged_in'):
        cur = db()
        cur.execute("SELECT * FROM doctor")
        all_doct = cur.fetchall()
        if request.method == 'POST' and 'pat' in request.form and 'doct_id' in request.form:
            pat = request.form['pat']
            doct_id = request.form['doct_id']
            cur.execute("SELECT * FROM doctor WHERE id = %s",(doct_id,))
            doct_data = cur.fetchone()
            dept_id = doct_data['department_id']
            cur.execute("INSERT INTO patient(patient_name,department_id,doctor_id) VALUES(%s, %s, %s)",(pat,dept_id,doct_id))
            mysql.connection.commit()
            alerts = "Patient record has been created successfully."
            return redirect(url_for('adashboard',alerts=alerts))
        return render_template('admin/createpatient.html', all_doct = all_doct)
    else:
        return redirect(url_for('adlogin'))

# Admin Create Medicine
@app.route('/acreatemed', methods=['GET', 'POST'])
def acreatemed():
    if session.get('adlogged_in'):
        if request.method == 'POST' and 'med' in request.form and 'stock' in request.form:
            med = request.form['med']
            stock = request.form['stock']
            cur = db()
            cur.execute("SELECT * FROM medicine WHERE medicine_name = %s",(med,))
            med_data = cur.fetchone()
            if med_data:
                alertd = "This medicine already exists. Please try another one."
                return render_template('/admin/createmedicine.html', alertd = alertd)
            else:
                cur.execute("INSERT INTO medicine(medicine_name,in_stock) VALUES(%s,%s)",(med,stock))
                mysql.connection.commit()
                alerts = "Medicine record has been created successfully."
                return redirect(url_for('adashboard',alerts=alerts))
        return render_template('/admin/createmedicine.html')
    else:
        return redirect(url_for('adlogin'))

# Admin Medicines List
@app.route('/amedlist')
def amedlist():
    if session.get('adlogged_in'):
        cur = db()
        cur.execute("SELECT * FROM medicine")
        all_med = cur.fetchall()
        if request.args.get('alerts'):
            alerts = request.args.get('alerts')
            return render_template('admin/medicinelist.html', all_med = all_med, alerts = alerts)
        return render_template('admin/medicinelist.html', all_med = all_med)
    else:
        return redirect(url_for('adlogin'))

#   Admin Edit Medicine
@app.route('/aeditmed', methods=['GET', 'POST'])
def aeditmed():
    if session.get('adlogged_in'):
        if request.args.get('med_id'):
            med_id = request.args.get('med_id')
            cur = db()
            cur.execute("SELECT * FROM medicine WHERE id = %s",(med_id,))
            med_data = cur.fetchone()
            return render_template('admin/editmedicine.html', med_data = med_data)
        if request.method == 'POST' and 'med' in request.form and 'stock' in request.form and 'med_id' in request.form:
            med = request.form['med']
            stock = request.form['stock']
            med_id = request.form['med_id']
            cur = db()
            cur.execute("SELECT * FROM medicine WHERE id = %s",(med_id,))
            med_data = cur.fetchone()
            cur.execute("SELECT * FROM medicine WHERE medicine_name = %s AND id != %s",(med,med_id))
            already_med_data = cur.fetchone()
            if already_med_data:
                alertd = "Medicine already exists. Please try with another one."    
                return render_template('admin/editmedicine.html', med_data = med_data, alertd = alertd)
            else:
                cur.execute("UPDATE medicine SET medicine_name = %s, in_stock = %s WHERE id = %s",(med,stock,med_id))
                mysql.connection.commit()
                alerts = "Medicine record has been updated successfully."
                return redirect(url_for('amedlist',alerts = alerts))
    else:
        return redirect(url_for('adlogin'))

#   Admin Delete Medicine
@app.route('/adeletemed', methods=['GET', 'POST'])
def adeletemed():
    if session.get('adlogged_in'):
        if request.args.get('med_id'):
            med_id = request.args.get('med_id')
            cur = db()
            cur.execute("DELETE FROM medicine WHERE id = %s",(med_id,))
            mysql.connection.commit()
            alerts = "Medicine record has been deleted successfully."
            return redirect(url_for('amedlist',alerts = alerts))
    else:
        return redirect(url_for('adlogin'))

#   Admin Patients List
@app.route('/apatlist', methods=['GET', 'POST'])
def apatlist():
    if session.get('adlogged_in'):
        cur = db()
        cur.execute("SELECT * FROM patient")
        all_pat = cur.fetchall()
        if request.args.get('alerts'):
            alerts = request.args.get('alerts')
            return render_template('admin/patientlist.html', all_pat = all_pat, alerts = alerts)
        return render_template('admin/patientlist.html', all_pat = all_pat)

#   Admin Edit Patient
@app.route('/aeditpat', methods=['GET', 'POST'])
def aeditpat():
    if session.get('adlogged_in'):
        if request.args.get('pat_id'):
            pat_id = request.args.get('pat_id')
            cur = db()
            cur.execute("SELECT * FROM patient WHERE id = %s",(pat_id,))
            pat_data = cur.fetchone()
            cur.execute("SELECT * FROM doctor")
            all_doct = cur.fetchall()
            return render_template('admin/editpatient.html', pat_data = pat_data, all_doct = all_doct)
        if request.method == 'POST' and 'pat' in request.form and 'doct_id' in request.form and 'pat_id' in request.form:
            pat = request.form['pat']
            doct_id = request.form['doct_id']
            pat_id = request.form['pat_id']
            cur = db()
            cur.execute("SELECT * FROM doctor WHERE id = %s",(doct_id,))
            doct_data = cur.fetchone()
            dept_id = doct_data['department_id']
            cur.execute("UPDATE patient SET patient_name = %s, doctor_id = %s, department_id = %s WHERE id = %s",(pat,doct_id,dept_id,pat_id))
            mysql.connection.commit()
            alerts = "Patient record has been updated successfully."
            return redirect(url_for('apatlist',alerts = alerts))

#   Admin Delete Patient
@app.route('/adeletepat', methods=['GET', 'POST'])
def adeletepat():
    if session.get('adlogged_in'):
        if request.args.get('pat_id'):
            pat_id = request.args.get('pat_id')
            cur = db()
            cur.execute("DELETE FROM patient WHERE id = %s",(pat_id,))
            mysql.connection.commit()
            alerts = "Patient record has been deleted successfully."
            return redirect(url_for('apatlist',alerts = alerts))

#   Admin Doctors List
@app.route('/adoclist', methods=['GET', 'POST'])
def adoclist():
    if session.get('adlogged_in'):
        cur = db()
        cur.execute("SELECT * FROM doctor")
        all_doct = cur.fetchall()
        if request.args.get('alerts'):
            alerts = request.args.get('alerts')
            return render_template('admin/doctorlist.html', all_doct = all_doct, alerts = alerts)
        return render_template('admin/doctorlist.html', all_doct = all_doct)

#   Admin Edit Doctor
@app.route('/aeditdoc', methods=['GET', 'POST'])
def aeditdoc():
    if session.get('adlogged_in'):
        if request.args.get('doct_id'):
            doct_id = request.args.get('doct_id')
            cur = db()
            cur.execute("SELECT * FROM doctor WHERE id = %s",(doct_id,))
            doct_data = cur.fetchone()
            cur.execute("SELECT * FROM department")
            all_dept = cur.fetchall()
            return render_template('admin/editdoctor.html', doct_data = doct_data, all_dept = all_dept)
        if request.method == 'POST' and 'doct' in request.form and 'dept_id' in request.form and 'doct_id' in request.form:
            doct = request.form['doct']
            dept_id = request.form['dept_id']
            doct_id = request.form['doct_id']
            cur = db()
            cur.execute("UPDATE doctor SET doctor_name = %s, department_id = %s WHERE id = %s",(doct,dept_id,doct_id))
            mysql.connection.commit()
            alerts = "Doctor record has been updated successfully."
            return redirect(url_for('adoclist',alerts = alerts))

#   Admin Delete Doctor
@app.route('/adeletedoc', methods=['GET', 'POST'])
def adeletedoc():
    if session.get('adlogged_in'):
        if request.args.get('doct_id'):
            doct_id = request.args.get('doct_id')
            cur = db()
            cur.execute("DELETE FROM doctor WHERE id = %s",(doct_id,))
            mysql.connection.commit()
            cur.execute("DELETE FROM patient WHERE doctor_id = %s",(doct_id,))
            mysql.connection.commit()
            alerts = "Doctor record has been deleted successfully."
            return redirect(url_for('adoclist',alerts = alerts))

#   Admin Department List
@app.route('/adeptlist', methods=['GET', 'POST'])
def adeptlist():
    if session.get('adlogged_in'):
        cur = db()
        cur.execute("SELECT * FROM department")
        all_dept = cur.fetchall()
        if request.args.get('alerts'):
            alerts = request.args.get('alerts')
            return render_template('admin/departmentlist.html', all_dept = all_dept, alerts = alerts)
        return render_template('admin/departmentlist.html', all_dept = all_dept)

#   Admin Delete Department
@app.route('/adeletedept', methods=['GET', 'POST'])
def adeletedept():
    if session.get('adlogged_in'):
        if request.args.get('dept_id'):
            dept_id = request.args.get('dept_id')
            cur = db()
            cur.execute("DELETE FROM department WHERE id = %s",(dept_id,))
            mysql.connection.commit()
            cur.execute("DELETE FROM doctor WHERE department_id = %s",(dept_id,))
            mysql.connection.commit()
            cur.execute("DELETE FROM patient WHERE department_id = %s",(dept_id,))
            mysql.connection.commit()
            alerts = "Department record has been deleted successfully."
            return redirect(url_for('adeptlist',alerts = alerts))


#   Admin logout
@app.route('/adlogout')
def adlogout():
    session.pop('adlogged_in', None)
    session.pop('admin_id', None)
    return redirect(url_for('adlogin'))

#   Get deprtment name
def get_dpartment_name(dept_id):
    cur = db()
    cur.execute("SELECT * FROM department WHERE id = %s",(dept_id,))
    dept_data = cur.fetchone()
    dept_name = dept_data['department_name']
    return dept_name
app.jinja_env.globals.update(get_dpartment_name=get_dpartment_name)

#   Get doctor name
def get_doctor_name(doct_id):
    cur = db()
    cur.execute("SELECT * FROM doctor WHERE id = %s",(doct_id,))
    doct_data = cur.fetchone()
    doct_name = doct_data['doctor_name']
    return doct_name
app.jinja_env.globals.update(get_doctor_name=get_doctor_name)

#   Get doctor option selected
def doctor_option_selected(pat_doc_id,doct_id):
    if pat_doc_id == doct_id:
        return 'selected'
app.jinja_env.globals.update(doctor_option_selected=doctor_option_selected)

#   Get department option selected
def department_option_selected(doc_dep_id, dept_id):
    if doc_dep_id == dept_id:
        return 'selected'
app.jinja_env.globals.update(department_option_selected=department_option_selected)

#   Get Patient Name
def get_patient_name_by_id(pat_id):
    cur = db()
    cur.execute("SELECT * FROM patient WHERE id = %s",(pat_id,))
    pat_data = cur.fetchone()
    pat_name = pat_data['patient_name']
    return pat_name
app.jinja_env.globals.update(get_patient_name_by_id=get_patient_name_by_id)

# Get patient Doctor
def get_doctor_name_by_patient_id(pat_id):
    cur = db()
    cur.execute("SELECT * FROM patient WHERE id = %s",(pat_id,))
    pat_data = cur.fetchone()
    doct_id = pat_data['doctor_id']
    cur.execute("SELECT * FROM doctor WHERE id = %s",(doct_id,))
    doct_data = cur.fetchone()
    doct_name = doct_data['doctor_name']
    return doct_name
app.jinja_env.globals.update(get_doctor_name_by_patient_id=get_doctor_name_by_patient_id)

#   Get patient department
def get_patient_department_by_id(pat_id):
    cur = db()
    cur.execute("SELECT * FROM patient WHERE id = %s",(pat_id,))
    pat_data = cur.fetchone()
    dept_id = pat_data['department_id']
    cur.execute("SELECT * FROM department WHERE id = %s",(dept_id,))
    dept_data = cur.fetchone()
    dept_name = dept_data['department_name']
    return dept_name
app.jinja_env.globals.update(get_patient_department_by_id=get_patient_department_by_id)