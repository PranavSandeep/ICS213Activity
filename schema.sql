PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Lots (
    lot_no INTEGER PRIMARY KEY,
    rate REAL NOT NULL CHECK (rate >= 0),
    free INTEGER NOT NULL DEFAULT 1 CHECK (free IN (0, 1))
);

CREATE TABLE IF NOT EXISTS Cars (
    registration_no TEXT PRIMARY KEY,
    model TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Customers (
    token_no INTEGER PRIMARY KEY AUTOINCREMENT,
    registration_no TEXT NOT NULL,
    lot_no INTEGER NOT NULL,
    phone_no CHAR(10) NOT NULL,
    time_booked TEXT NOT NULL,

    FOREIGN KEY (registration_no)
        REFERENCES Cars(registration_no)
        ON DELETE CASCADE,

    FOREIGN KEY (lot_no)
        REFERENCES Lots(lot_no)
        ON DELETE CASCADE
);