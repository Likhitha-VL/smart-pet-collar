from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import pickle
import requests
from fol import create_map

# =============================
# Load trained model
# =============================
model = pickle.load(open("rf.pkl", "rb"))



app = Flask(__name__)

# =============================
# Ensure pet_records.db and records table exist
# =============================
conn = sqlite3.connect("pet_records.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pet_type TEXT,
    heart_rate REAL,
    temperature REAL,
    spo2 REAL,
    condition TEXT,
    dos TEXT,
    donts TEXT,
    latitude REAL,
    longitude REAL
)
""")
conn.commit()
conn.close()

# =============================
# Helper function to fetch live data
# =============================
def get_live_data():
    response = requests.get("https://aislyntech.com/Api/y-get")
    data = response.json()['data'][-1]  # latest entry
    hb = int(data['heart_rate'])
    Temp = float(data['temperature'])
    oxy = int(data['spo2'])
    Lati = float(data['latitude'])
    Long = float(data['longitude'])
    return hb, Temp, oxy, Lati, Long


# =============================
# ROUTES
# =============================

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/aboutus')
def aboutus():
    return render_template('developers_page.html')


# =============================
# USER LOGIN
# =============================
@app.route('/userlog', methods=['GET', 'POST'])
def userlog():
    if request.method == 'POST':
        connection = sqlite3.connect('user_data.db')
        cursor = connection.cursor()
        name = request.form['name']
        password = request.form['password']

        query = "SELECT name, password FROM user WHERE name = ? AND password = ?"
        cursor.execute(query, (name, password))
        result = cursor.fetchall()
        connection.close()

        if not result:
            # invalid credentials
            return render_template('index.html', msg='Sorry, Incorrect Credentials Provided. Try Again')
        else:
            # ✅ redirect directly to prediction page after login
            return redirect(url_for('predictPage', name=name))

    return render_template('index.html')


# =============================
# USER REGISTRATION
# =============================
@app.route('/userreg', methods=['GET', 'POST'])
def userreg():
    if request.method == 'POST':
        connection = sqlite3.connect('user_data.db')
        cursor = connection.cursor()

        name = request.form['name']
        password = request.form['password']
        mobile = request.form['phone']
        email = request.form['email']

        cursor.execute("""CREATE TABLE IF NOT EXISTS user(
                          name TEXT, password TEXT, mobile TEXT, email TEXT)""")
        cursor.execute("INSERT INTO user VALUES (?, ?, ?, ?)", (name, password, mobile, email))
        connection.commit()
        connection.close()

        return render_template('index.html', msg='Successfully Registered')

    return render_template('index.html')


@app.route('/logout')
def logout():
    return render_template('index.html')


# =============================
# PREDICTION PAGE
# =============================
@app.route("/predictPage", methods=['POST', 'GET'])
def predictPage():
    live_data = {}
    prediction = ""
    dos = []
    donts = []
    diet = []
    all_records = []

    # Get name from query string if redirected after login
    name = request.args.get('name', 'User')

    if request.method == 'POST':
        action = request.form.get("action")

        if action == "fetch_live":
            hb, Temp, oxy, Lati, Long = get_live_data()
            live_data = {"hb": hb, "Temp": Temp, "oxy": oxy, "Lati": Lati, "Long": Long}

        elif action == "predict":
            type_pet = int(request.form.get("type", 1))  # 0 = Cat, 1 = Dog
            pet = "Cat" if type_pet == 0 else "Dog"

            hb = float(request.form.get("hb", 0))
            Temp = float(request.form.get("Temp", 0))
            oxy = float(request.form.get("oxy", 0))
            if hb == 0 or Temp == 0 or oxy == 0:
                hb, Temp, oxy, Lati, Long = get_live_data()
            else:
                Lati = float(request.form.get("Lati", 0))
                Long = float(request.form.get("Long", 0))

            pred = model.predict([[type_pet, hb, Temp, oxy]])[0]
            pred_clean = str(pred).strip().capitalize()

            advice_mapping = {
                "Normal": {
                    "Dos": ["Maintain feeding schedule", "Provide water", "Exercise daily", "Vaccinate"],
                    "Don'ts": ["Don't overfeed", "Don't skip vet check-ups"],
                    "Diet": ["Regular balanced diet"]
                },
                "Fever": {
                    "Dos": ["Keep hydrated", "Warm resting place", "Monitor temperature", "Vet if persists"],
                    "Don'ts": ["No human meds", "No cold drafts", "Don't ignore lethargy"],
                    "Diet": ["Light, easily digestible food", "Plenty of fluids"]
                },
                "Hypothermia": {
                    "Dos": ["Warm blankets", "Keep indoors", "Monitor temp", "Vet care"],
                    "Don'ts": ["No direct heat", "Don't leave outside", "Don't ignore shivering"],
                    "Diet": ["High-calorie warm food"]
                },
                "Tachycardia": {
                    "Dos": ["Monitor heart rate", "Keep calm", "Comfortable resting place", "Vet advice"],
                    "Don'ts": ["No loud play", "Don't skip vet", "Don't ignore rapid heartbeat"],
                    "Diet": ["Light, low-salt diet"]
                },
                "Bradycardia": {
                    "Dos": ["Observe lethargy", "Keep warm", "Vet immediately", "Monitor heart rate"],
                    "Don'ts": ["Don't ignore slow heart rate", "Don't overexert"],
                    "Diet": ["Nutritious food with moderate activity"]
                },
                "Hypoxemia": {
                    "Dos": ["Ensure oxygen", "Monitor breathing", "Keep calm", "Emergency vet care"],
                    "Don'ts": ["Don't ignore labored breathing", "Don't leave poorly ventilated"],
                    "Diet": ["Easily digestible, energy-rich food"]
                }
            }

            advice = advice_mapping.get(pred_clean, {})
            dos = advice.get("Dos", [])
            donts = advice.get("Don'ts", [])
            diet = advice.get("Diet", [])

            # Save prediction to database
            conn = sqlite3.connect("pet_records.db")
            c = conn.cursor()
            c.execute('''INSERT INTO records (pet_type, heart_rate, temperature, spo2, condition, dos, donts, latitude, longitude)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (pet, hb, Temp, oxy, pred_clean, ", ".join(dos), ", ".join(donts), Lati, Long))
            conn.commit()
            conn.close()
            prediction = pred_clean

        elif action == "view_db":
            conn = sqlite3.connect("pet_records.db")
            c = conn.cursor()
            c.execute("SELECT * FROM records ORDER BY id DESC")
            all_records = c.fetchall()
            conn.close()

    if not live_data:
        hb, Temp, oxy, Lati, Long = get_live_data()
        live_data = {"hb": hb, "Temp": Temp, "oxy": oxy, "Lati": Lati, "Long": Long}

    return render_template(
        "predict.html",
        name=name,
        live_data=live_data,
        prediction=prediction,
        dos=dos,
        donts=donts,
        diet=diet,
        all_records=all_records
    )


# =============================
# Run App
# =============================
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
