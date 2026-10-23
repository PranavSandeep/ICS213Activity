import datetime
import json
import sqlite3
from flask import Flask, render_template, request, jsonify
from dateutil import parser

app = Flask(__name__)

RATE = 10

def get_db():
    db = sqlite3.connect("parking.db")
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db

@app.route("/admin")
def admin():
    return render_template("index_finalm.html", admin=True)

@app.route("/")
def home():
    return render_template(r"index_finalm.html", admin=False)

@app.route("/lots")
def get_lots():
    db = get_db()
    lots = db.execute("SELECT * FROM Lots").fetchall()
    db.close()

    return jsonify([dict(lot) for lot in lots])

@app.route("/book", methods=["POST"])
def book():
    db = get_db()
    data = request.get_json()
    lot_no = data["lot_no"]
    registration_no = data["registration_no"]
    registered_at = data["registered_at"]
    model = data["model"]
    phone_no = data['phone']


    print(data)

    db.execute("UPDATE Lots SET free = 0 WHERE lot_no = ?", (lot_no,))

    cursor = db.execute(
        """
        INSERT INTO Cars
        (registration_no, model)
        VALUES (?, ?)
        """,
        (registration_no, model)
    )

    cursor = db.execute(
        """
        INSERT INTO Customers
        (registration_no, lot_no, time_booked, phone_no)
        VALUES (?, ?, ?, ?)
        """,
        (registration_no, lot_no, registered_at, phone_no)
    )

    token_no = cursor.lastrowid
    db.commit()
    db.close()

    return jsonify({"message": "Lot booked succesfully", "token_no": token_no})


@app.route('/pullout', methods=["POST"])
def pullout():
    db = get_db()
    data = request.get_json()

    lot_no = data["lot_no"]
    lot_rate = data["lot_rate"]

    row = db.execute("""
        SELECT
            L.lot_no,
            L.rate,
            L.free,
            C.token_no,
            C.registration_no,
            C.time_booked
        FROM Lots L
        JOIN Customers C
            ON C.lot_no = L.lot_no
        WHERE L.lot_no = ?
    """, (lot_no,)).fetchone()

    token_no = row[3]

    if token_no != data["token_no"]:
        return jsonify({"message" : "Incorrect Token for the lot number"})

    booked_date = parser.parse(row[5])

    print(booked_date, type(booked_date))

    date_time = datetime.datetime.now(datetime.timezone.utc)

    time_difference = date_time - booked_date
    time_difference = time_difference.total_seconds()

    time_difference //= 60

    rate = time_difference * lot_rate
    rate = max(lot_rate, rate)


    db.execute("""
        DELETE FROM Cars WHERE registration_no = ?""", (row[4],))

    db.execute("UPDATE Lots SET free = 1 WHERE lot_no = ?", (lot_no,))

    db.commit()
    db.close()


    return jsonify({"message": "Lot checked out succesfully", "rate": rate})



@app.route("/details", methods=["POST"])
def details():
    db = get_db()
    data = request.get_json()
    lot_no = data["lot_no"]

    row = db.execute("""
            SELECT
                L.lot_no,
                L.rate,
                L.free,
                C.token_no,
                C.registration_no,
                C.time_booked,
                C.phone_no
            FROM Lots L
            JOIN Customers C
                ON C.lot_no = L.lot_no
            WHERE L.lot_no = ?
        """, (lot_no,)).fetchone()

    return jsonify({"token_no": row[3], "registration_no": row[4], "phone_no": row[-1]})



@app.route("/remove", methods=["POST"])
def remove():
    db = get_db()
    data = request.get_json()
    lot_no = data["lot_no"]

    db.execute("UPDATE Lots SET free = 1 WHERE lot_no = ?", (lot_no,))

    db.commit()
    db.close()

    return jsonify({"message": "Lot booked succesfully"})




if __name__ == "__main__":
    app.run(debug=True)