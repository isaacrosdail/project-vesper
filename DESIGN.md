

## Service / Repo / Controller pattern

Problem:
- Routes mixing orchestration, business logic, and data access seemed like a problem to me before they became a problem:
    1. Parsing route code as an 'overview' of what's going on becomes difficult.
    2. Maintaining said code requires such parsing, and in turn also becomes more difficult and error-prone.
    3. Core logic that's reused in multiple routes is not able to be reused effectively unless extracted to helpers which live elsewhere.
    4. Testing becomes difficult:
        - Rather than having piecewise functionality extracted into single-responsibility, more tightly-scoped helpers, tests would need to mock (and therefore take into consideration) each piece of what's occurring throughout the entire route.

Decision:
- Routes should contain only the "synopsis-view" of what's happening, handling specific routing (I mean it's in the name!), delegating actual logic to helpers.
- This is in accordance with the MVC Model-View-Controller pattern: Models (Repository), View (Templates), Controller (Routes).
    1. That means repository access ought to be relegated to its own wing, likewise for service/business logic.

Why it was right:
- This keeps routes as tidy and legible as possible, where helper functions can "read as English".
    1. Helper functions can also then be streamlined to fit their specific overarching needs, which means fixing/altering them fixes/alters them EVERYWHERE - no "did I get em all?"
    2. Ensures that logic can be "handled once, handled everywhere". This is especially important when handling timezones, as they're easy to get wrong.
    3. Massive reduction in boilerplate for common operations. Rather than inlining it, we can extract and re-invoke with different parameters.
    4. Even though this approach does incur more work upfront, and more files, it keeps responsibilities more cleanly partitioned, especially in the long-term.
    5. The repository layer is able to be "dumb", assuming UTC for timezone, and delegating the responsibility to managing whether the timezone we use is correct to the service layer.
        - This makes sense, as the service layer's role is to sort out the business/domain logic.

Concrete example:
- Take our route for the tasks dashboard:
```python
@tasks_bp.get("/dashboard")
@login_plus_session
def dashboard(session: "Session") -> tuple[str, int]:
    tasks_params = get_table_params("tasks", "due_date")

    tasks_service = create_tasks_service(
        session, current_user.id, current_user.timezone
    )
    tasks = tasks_service.task_repo.get_all()
    tasks = sort_by_field(tasks, tasks_params["sort_by"], tasks_params["order"])

    viewmodel = [TaskViewModel(t, current_user.timezone) for t in tasks]

    ctx = {
        "tasks_params": tasks_params,
        "task_headers": TaskPresenter.build_columns(),
        "tasks": viewmodel,
    }
    return render_template("tasks/dashboard.html", **ctx), 200
```
Here, we do a handful of concrete, distinct steps:
1. Parse/get the table parameters from the request's query parameters.
2. Initialize our tasks service, which itself contains the necessary repository instantiations for our operations.
3. Via service's access to the repository, we fetch all tasks.
4. Then sort by field.
5. We run all of our tasks through our TaskViewModel, which does the final processing to ensure our data is formatted as desired for display in the template.
6. Finally, we build the context (ctx) for our template and render it.

If all of this were to be in the route itself, it would be much, much more difficult to parse, and even harder to test its components to ensure they work.
With functionality extracted into helpers, we're able to moreso declare what we wish to happen in the route (sort_by_field, get_table_params, etc) and focus on the higher-level overview of what needs to happen, rather than be in the trenches inlining that ourselves.

---

## Viewmodels

Problem: Nothing really catches our mistakes in Markup/Jinja. As such, we want minimal modulation/handling to live in our templates.
    - There are no hints nor any enforcements from either our IDE or "baked in" to the language itself: HTML is too forgiving to flag issues, and Jinja doesn't provide hints.
    - If I made a mistake, which is inevitable, nothing is there to catch me or flag that I did.

Decision:
- Create a viewmodels layer whose job it is to modulate data for display. This sits in between our routes which call it, and our templates whose fields it feeds.

Why it was right:
- With a viewmodels.py for each module, we can handle this instead in an environment where such issues DON'T go unflagged:
    - Types and mismatches will be caught and flagged by Mypy.
    - Runtime errors will catch `getattr` mismatches for fields we're roping in.
    - We'll receive hints from IDE/editor

Example:
This is an issue I still have with macros:
```html
{% call(item, headers) ui.responsive_table('Tasks', task_headers, tasks, 'tasks', 'tasks', tasks_params, sortable=True) %}
        <td class="{{ headers[0].priority }}" data-item-id="{{ item.id }}" data-module="tasks" data-subtype="tasks" data-field="name"
```
For example, here: Did we pass in the correct parameters, of the right types? Is the function name misspelled? Who knows! Better go check the macro definition for that!
Contrast that with the below:
```python
# We can leverage Mypy, enforcing the types these ought to be:
class TransactionViewModel(BaseViewModel):
    product_id: int
    price_at_scan: float
    quantity: int

    # If any field is missing or there's a typo, we'll receive actual runtime errors:
    def __init__(self, txn: Transaction, tz: str) -> None:
        fields = { "product_id", "price_at_scan", "quantity" }
        for name in fields:
            setattr(self, name, getattr(txn, name))

    # And we can combine multiple fields to be displayed as one cell in our table, including
    # basic manipulation to display total price:
    @property
    def price_label(self) -> str:
        total_price = self.price_at_scan * self.quantity
        return f"${total_price:.2f} ({self.quantity}x)"
```
At multiple points, our IDE/Mypy/etc will expose mismatches and potential issues that markup/Jinja will silently ignore.

---


## Tasks Web Visualizer

### Why this Feature Exists

1. Normal, flat lists can't express relationships between tasks.
2. With a web visualization, we can express actual hierarchy, at multiple depths at a time, of tasks and their subtasks.
    This context expression buys us more than just visual hierarchy though:
        1. Priority is encoded into the actual color of the nodes themselves
        2. (PLANNED) Facilitates performing calculations for cumulative time for a task, meaning:
            - Make bed (10mins) + Eat breakfast (10mins) -- both required for --> Get ready for school
            - This way, we can display (Est: 20mins) for the last task there, enabling compression of context in a natural, visual way


### Why an association table for task relationships/dependencies?

Using self-referential FKeys on our Tasks table alone doesn't work for the potentially many-to-many relationships that we can have with subtasks <-> supertasks.
This is because one column in our table only holds one value per row => subtask_id/supertask_id.

Association tables CAN handle this many-to-many relationship because each relationship can be represented as its own distinct entry of:
(subtask_id, supertask_id)
More relationships just means adding more entries to the table, rather than redesigning the Tasks model itself.


### Why D3? Why not Canvas?
1. Manual SVG manipulation:
    - With canvas, there's difficulty in managing click events. The "thing" (each node, link, etc) doesn't exist anymore:
        1. I'd have to manipulate raw pixel values, rather than working with SVG elements and groups in the DOM.
        2. We'd need to do manual hit detection: checking if the click coordinates were within the bounds of each thing we rendered on screen. There would be no elements to simply attach listeners to.
2. A note on the performance difference:
    - Canvas IS undoubtedly faster, but that comes at the cost of the above: It's faster precisely because once the image is rendered, that's it. There's no "memory" of what each "thing"
    is anymore.
    - D3 performance issues, to my understanding, seem to arrive in the "thousands of objects/elements" territory. I can't imagine a user having thousands of active tasks! Therefore, the performance tradeoff feels, in my use case, not in the realm of concern.


#### Stuff to iron out:
- zoom, panning limits, "web as a whole page" idea from Obsidian to fix that.
