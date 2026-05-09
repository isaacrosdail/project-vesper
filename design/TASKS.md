
# Covers:
- Web visualizer
- Lex strings for task position indexing (TODO)


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