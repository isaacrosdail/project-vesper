
import inspect
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from app.modules.tasks.models import Task

from app.shared.view_mixins import BasePresenter, TimestampedViewMixin


class TaskPresenter(BasePresenter):
    VISIBLE_COLUMNS: ClassVar[list[str]] = [
        "name", "priority", "is_frog", "due_date"
    ]
    COLUMN_CONFIG: ClassVar[dict[str, dict[str, str]]] = {
        "id": {"label": "Task ID", "priority": "desktop-only"},
        "name": {"label": "Task", "priority": "essential"},
        "is_done": {"label": "Status", "priority": "essential"},
        "priority": {"label": "Priority", "priority": "essential"},
        "is_frog": {"label": "'Frog Task'?", "priority": "desktop-only"},
        "due_date": {"label": "Due Date", "priority": "essential"},
        "created_at": {"label": "Created", "priority": "desktop-only"},
        "completed_at": {"label": "Completed", "priority": "desktop-only"}
    }

class TaskViewModel(TimestampedViewMixin):
    def __init__(self, task: "Task", tz: str) -> None:
        import sys
        # obj = descriptor object
        # name = name of the field/column in task class (id, name, subtype, etc.)
        # inspect.getmembers(task.__class__) returns EVERYTHING on the class:
        # [
        #     ('id', <sqlalchemy...>),              # SQLAlchemy column
        #     ('name', <sqlalchemy...>),            # SQLAlchemy column  
        #     ('subtype', <property object>),       # @property ← Your target
        #     ('created_at_local', <property object>), # @property ← Your target
        #     ('__init__', <function>),             # Method
        #     ('__str__', <function>),              # Method
        #     ('query', <sqlalchemy...>),           # SQLAlchemy class attribute
        #     ('__tablename__', 'tasks'),           # Class variable
        #     # ... tons more
        # ]
        # "For every member of the Task class, if it's a property descriptor (and not private),
        #  copy its computed value to my ViewModel."
        for name, obj in inspect.getmembers(task.__class__):
            # Check if obj is an instance of 'property' (ie, an instance of a property descriptor)
            # and doesn't start with _ (to ignore dunders?)
            if isinstance(obj, property) and not name.startswith('_'):
                # Set this TaskViewModel's instance's field thing to that value?
                # 
                setattr(self, name, getattr(task, name))
                print(f"{name} {obj} {getattr(task, name)} task name: {getattr(task, name)}", file=sys.stderr)
        self.id = task.id
        self.name = task.name
        self.is_done = task.is_done
        self.priority = task.priority
        self.is_frog = task.is_frog
        self.due_date = task.due_date
        self.completed_at = task.completed_at
        self.tags = task.tags
        self._tz = tz

    @property
    def priority_label(self) -> str:
        return f"{self.priority.value.title()}"

    @property
    def frog_label(self) -> str:
        return "Yes" if self.is_frog else ""

    @property
    def due_label(self) -> str:
        return self.format_due_label()
