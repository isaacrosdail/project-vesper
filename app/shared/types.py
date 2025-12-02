from enum import Enum
from functools import total_ordering
from typing import Self


@total_ordering  
class OrderedEnum(Enum):
    """
    Base for sortable enums.
    Current hacky usage: 
    
    class MY_ENUM(OrderedEnum):
        ...

    Below enum class, define MY_ENUM.sort_order as a list[str]
    """
    
    def __lt__(self, other: Self) -> bool:
        if self.__class__ is not other.__class__:
            return NotImplemented
        # Access via __class__ attribute directly
        order = getattr(self.__class__, 'sort_order', None)
        if not order:
            raise NotImplementedError(f"{self.__class__.__name__} must define sort_order")
        return order.index(self.name) < order.index(other.name)