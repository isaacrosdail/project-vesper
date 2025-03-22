# Handles DB setup/functionality & grocery related DB functions
from core.database import get_session, engine
from sqlalchemy import text

# Setup function for groceries portion of database
## Run this once upon boot up
def setup_schema():
	conn = engine.connect()  # Handshake - encapsulates DBAPI, connection string, pooling config?
	conn.execute(text(
		"CREATE TABLE IF NOT EXISTS groceries (name str, price float, grams int)"
		)) # executes statement
	conn.commit() # applies change(s) to database

# Starts a session with the respective database
session = get_session()
session.execute(
	text('INSERT INTO groceries (name, price, grams) VALUES (:name, :price, :grams)'),
	{"name": "Strawberry Jam", "price": 5.49, "grams": 250}
)
session.commit()