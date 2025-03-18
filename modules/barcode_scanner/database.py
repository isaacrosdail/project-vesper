# Handles DB setup/functionality & grocery related DB functions

from sqlalchemy import create_engine, text

# Force groceries.db to be relative to database.py
import os
DB_PATH = os.path.join(os.path.dirname(__file__), "groceries.db")

engine = create_engine(f'sqlite:///{DB_PATH}', echo=True) # Echo for debugging/learning purposes
# Now we need to connect to the db through this engine
conn = engine.connect()
# Executes the statement
conn.execute(text("CREATE TABLE IF NOT EXISTS groceries (name str, price float, grams int)"))
# but to actually apply the change to the db, do:
conn.commit()


from sqlalchemy.orm import Session

# Starts a session with the respective database
session = Session(engine)

session.execute(
	text('INSERT INTO groceries (name, price, grams) VALUES (:name, :price, :grams)'),
	{"name": "Strawberry Jam", "price": 5.49, "grams": 250}
)
session.commit()