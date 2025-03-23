# Handles DB setup/functionality & grocery related DB functions
from core.database import get_session, engine
from sqlalchemy import text

# Setup function for groceries portion of database
## Run this once upon boot up
def setup_schema():
	print("[groceries] Running schema setup...")
	conn = engine.connect()  # Handshake - encapsulates DBAPI, connection string, pooling config?
	conn.execute(text(
		"CREATE TABLE IF NOT EXISTS groceries (name str, price float, grams int)"
		)) # executes statement
	conn.commit() # applies change(s) to database
	print("[groceries] Table creation committed.")

def get_all_products():
	session = get_session()
	result = session.execute(text("SELECT * FROM groceries"))
	session.close()
	return result

def add_product(name, price, grams):
	# Starts a session with the respective database
	session = get_session()
	session.execute(
		text('INSERT INTO groceries (name, price, grams) VALUES (:name, :price, :grams)'),
		{"name": name, "price": price, "grams": grams}
	)
	session.commit()
	session.close()