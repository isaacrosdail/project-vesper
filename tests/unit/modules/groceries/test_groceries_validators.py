from decimal import Decimal

from app._infra.database import db_session
from app.modules.groceries.validators import validate_product_data


# Happy path
def test_parse_and_validate_form_data():
    pass
    # # Arrange
    # product_data = {
    #     "name": "Test Product",
    #     "barcode": "123456789", 
    #     "net_weight": "100.5",      # String from form
    #     "unit_type": "g",           # String from form
    # }

    # # Act
