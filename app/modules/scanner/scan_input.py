# Shared scanner logic here?
## Idea: use evdev on Pi (unfortunately evdev is Linux-only supported via /dev/input/event)

''' Check OS type to determine whether to use real scan loop (Pi/Linux) or simulate scan loop (Windows)
from sys import platform

if platform == "linux":
    real_scan_loop()
elif platform == "win32":
    simulate_scan_loop(callback)



def simulate_scan_loop(callback):
    while True:
        fake = input("Simulate barcode: ")
        callback(fake)

#####################################
# Uses **kwargs to take in optional data (ie., from forms)
# Now used for scanner barcode input only

def process_scanned_barcode(session, barcode, **product_data):
	product = lookup_barcode(session, barcode)

	if product:
		add_transaction(session, product, quantity=1, price_at_scan=product.price, net_weight=product.net_weight)
		return "added_transaction"

	return "new_product"
'''
####################################