from flask import Flask, request, render_template, redirect, url_for, flash, session
from functools import wraps
from datetime import datetime
import pickle
import numpy as np

import sqlite3
conn = sqlite3.connect('db/lung_disease.db', check_same_thread=False)

app = Flask(__name__)
app.config['SECRET_KEY'] = '8IR4M7-6789876-654ERTYWVCFD'

# Load the model
with open('model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/login_user', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM User where email = ? and password = ?", (email, password))
        data = cursor.fetchone()
        if data is not None:
            session['std_logged_in'] = True
            session['uid'] = data[0]
            session['uname'] = data[1]+' '+data[2]
            session['fname'] = data[1]
            session['lname'] = data[2]
            session['email'] = data[3]
            flash('You are now logged in', 'success')
            return redirect(url_for('user'))
        else:
            error = 'Invalid login'
            return render_template('login_user.html', error=error)
    return render_template('login_user.html')

def is_user_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'std_logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login!', 'danger')
            return redirect(url_for('login_user'))
    return wrap

def is_admin_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'admin_logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login!', 'danger')
            return redirect(url_for('login_admin'))
    return wrap

@app.route('/login_admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Admin where email = ? and password = ?", (email, password))
        data = cursor.fetchone()
        if data is not None:
            session['uid'] = data[0]
            session['uname'] = data[1]
            session['email'] = data[2]
            session['admin_logged_in'] = True
            flash('You are now logged in', 'success')
            return redirect(url_for('admin'))
        else:
            error = 'Invalid login'
            return render_template('login_admin.html', error=error)
    return render_template('login_admin.html')

@app.route('/admin')
@is_admin_logged_in
def admin():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM User order by id desc")
    data = cursor.fetchall()
    cursor.close()
    return render_template('dashboard_admin.html', users=data)

@app.route('/user', methods=['GET', 'POST'])
@is_user_logged_in
def user():
    return render_template('dashboard_user.html')

@app.route('/predict', methods=['GET', 'POST'])
@is_user_logged_in
def predict():
    if request.method == 'POST':
        location = request.form['location']
        ethnicity = request.form['ethnicity']
        aqi = int(request.form['aqi'])
        smokers_percentage = int(request.form['smokers_percentage'])

        # Map ethnicity to encoded value
        ethnicity_map = {
            'Asian': -0.02,              # Slightly reduce risk
            'Hispanic': 0.01,            # Slightly increase risk
            'African-American': 0.03,    # Slightly increase risk
            'Caucasian': -0.01           # Slightly reduce risk
        }

        ethnicity_encoded = ethnicity_map.get(ethnicity, -1)

        if ethnicity_encoded == -1:
            flash('Invalid ethnicity', 'danger')
            return redirect(url_for('predict'))

        # Predict probability
        features = np.array([[ethnicity_encoded, aqi, smokers_percentage]])
        probability = model.predict_proba(features)[0][1]
        
        # Determine risk level
        if probability <= 0.3:
            risk_level = "Low Risk" 
        elif 0.3 < probability <= 0.7:
            risk_level = "Medium Risk"
        else:
            risk_level = "High Risk"
        
        # Store in database
        cursor = conn.cursor()
        cursor.execute('INSERT INTO predictions (location, ethnicity, aqi, smokers_percentage, probability) VALUES (?, ?, ?, ?, ?)',
                  (location, ethnicity, aqi, smokers_percentage, probability))
        conn.commit()
        cursor.close()

        flash(f"Lung Disease Risk Level: {risk_level} (Probability: {probability:.2f})", "success")
        return redirect(url_for('predict'))
    return render_template('predict.html')

@app.route('/view_history')
@is_admin_logged_in
def view_history():
    sql = "SELECT * FROM Predictions order by id"
    cursor = conn.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    return render_template('view_history.html', history=data)

@app.route("/logout")
def logout():
    if 'std_logged_in' or 'admin_logged_in' in session:
        session.clear()
    return redirect(url_for('index'))

@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        email = request.form['email']
        fname = request.form['fname']
        lname = request.form['lname']
        password = request.form['password']
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM User where email = ?", (email,))
        data = cursor.fetchone()
        if data is None:
            sql = 'INSERT INTO User(fname,lname,email,password) VALUES(?,?,?,?)'
            data_tuple = (fname, lname, email, password)
            cursor.execute(sql, data_tuple)
            conn.commit()
            cursor.close()
            flash('User registration successful', 'success')
            return render_template('register_user.html')
        else:
            flash('User with this email already exists!', 'danger')
    return render_template('register_user.html')

app.run(port=5000,debug=True)
if __name__ == '__main__':
    pass