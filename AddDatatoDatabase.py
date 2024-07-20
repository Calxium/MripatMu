import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceCertificate.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://mripatmu-5bfce-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

data = {

        "12345":
        {
            "name": "Afrijal Rizqi Ramadan",
            "major": "TI",
            "starting_year": 2020,
            "total_out": 0,
            "kelas": "11 A",
            "last_out_time": "2022-12-11 00:00:00"
        }

}

for key, value in data.items():
    ref.child(key).set(value)