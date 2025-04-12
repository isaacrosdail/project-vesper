# Entry point for Flask app ONLY

from app import create_app

## OLDER IMPORTS
import threading  ## For now, used for running background scanner input daemon

## Database handling stuff
from app.modules.groceries import repository as grocery_repo
from app.modules.scanner import scan_input ## For now, used for running background scanner input
from app.database import get_db_session

# Prototyping BARCODE SCANNER logic/handling
def handle_barcode_first(barcode):
    session = get_db_session()
    try:
        result = grocery_repo.handle_barcode(session, barcode)

        if result == "added_transaction":
            session.commit()
            return
        elif result == "new_product":
            session.close()
            # Redirect to 
        
        grocery_repo.handle_barcode(barcode)
        session.commit()
    finally:
        session.close()

# Start daemon to listen in background for barcode(s)
scanner_thread = threading.Thread(
    target=lambda: scan_input.simulate_scan_loop(handle_barcode_first),
    daemon=True
)
scanner_thread.start()
# # # # #

app = create_app()

if __name__ == "__main__":
    app.run(debug=True) # Remove this now that we have configs? CHECK