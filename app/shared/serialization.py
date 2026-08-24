from datetime import datetime
from decimal import Decimal

from flask.json.provider import DefaultJSONProvider


# jsonify internally calls json.dumps()
# When json.dumps() hits a type it doesn't know (datetime, Decimal), it calls
# a default() method. That's what we're writing here.
class CustomJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat(timespec="seconds")
        if isinstance(obj, Decimal):
            return round(float(obj), 2)
        return super().default(obj)

