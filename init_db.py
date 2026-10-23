import sqlite3

db = sqlite3.connect("parking.db")

with open("schema.sql", "r") as file:
    db.executescript(file.read())

db.executemany(
    "INSERT OR IGNORE INTO Lots (lot_no, rate) VALUES (?, ?)",
    [(1, 30), (2, 30), (3, 40), (4, 50), (5, 40), (6, 50)]
)


db.execute(
    "UPDATE Lots SET free = 1"
)

db.commit()
db.close()