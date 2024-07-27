import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("yourcertificate.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://database.firebaseio.com/"
})

ref = db.reference('Students')

data = {

        "19170":
        {
            "name": "Ahmad Hanif Zakaria",
            "major": "TI",
            "starting_year": 2020,
            "total_out": 0,
            "kelas": "12-6",
            "last_out_time": "2022-12-11 00:00:00"
        },
        "19342":
        {
            "name": "Mohammad Rahardian Atsil",
            "major": "TI",
            "starting_year": 2020,
            "total_out": 0,
            "kelas": "12-6",
            "last_out_time": "2022-12-11 00:00:00"
        },
        "19201":
        {
            "name": "Arkana Rizky Faviansyah",
            "major": "TI",
            "starting_year": 2020,
            "total_out": 0,
            "kelas": "12-6",
            "last_out_time": "2022-12-11 00:00:00"
        },
        "19167":
        {
            "name": "Aditya Rajadana",
            "major": "TI",
            "starting_year": 2020,
            "total_out": 0,
            "kelas": "12-6",
            "last_out_time": "2022-12-11 00:00:00"
        }

}

for key, value in data.items():
    ref.child(key).set(value)