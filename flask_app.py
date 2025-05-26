# Entry point for Flask app

from app import create_app

## Database handling stuff
from app.modules.groceries import repository as grocery_repo
from app.modules.scanner import scan_input ## For now, used for running background scanner input
from app.core.database import db_session

# Import DB stuff
from app.modules.groceries import models as grocery_models
from app.modules.tasks import models as tasks_models


'''
----- Prototyping BARCODE SCANNER logic/handling

import threading  ## Intended for background scanner input daemon

def handle_barcode_first(barcode):
    session = db_session()
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
'''

app = create_app()

if __name__ == "__main__":
    app.run()