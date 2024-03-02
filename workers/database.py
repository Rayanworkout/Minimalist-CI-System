import sqlite3


class DBWorker:
    ___instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        self.__conn = sqlite3.connect("tests.sqlite3")
        self.__cursor = self.__conn.cursor()
        self.__cursor.execute(
            """CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    age INTEGER
                )"""
        )
        self.__conn.commit()


# Insert data into the table
# cursor.execute("INSERT INTO employees (name, age) VALUES (?, ?)", ("John Doe", 30))

# # Fetch data
# cursor.execute("SELECT * FROM employees")
# rows = cursor.fetchall()
# for row in rows:
#     print(row)

# # Commit the changes
# conn.commit()

# # Close the cursor and the connection
# cursor.close()
# conn.close()
