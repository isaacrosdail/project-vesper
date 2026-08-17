// Queue via Linked list
// FIFO. Tracking head and tail enables O(1) time for enqueue (at tail) and dequeue (at head)
// This is possible because we always keep a reference to both head and tail
// And, unlike arrays, we do NOT have to shift every item in the list over on dequeue (which would be O(n) of course)
// Tradeoff is that we lose random access functionality of arrays, but queues don't need this anyway.

class QueueNode<T> {
    data: T;
    next: QueueNode<T> | null = null;

    constructor(val: T) {
        this.data = val
    }
}

/**
 * Queue implemented using a linked list for O(1) enqueue/dequeue.
 * 
 * Loses the random access of arrays, but queues don't need this anyway.
 */
export class Queue<T> {
    #head: QueueNode<T> | null;
    #tail: QueueNode<T> | null;
    #size: number;

    constructor() {
        this.#head = null
        this.#tail = null
        this.#size = 0
    }

    enqueue(val: T) {
        const node = new QueueNode(val)
        if (this.#size === 0) {
            this.#head = node
            this.#tail = node
        } else {
            this.#tail!.next = node
            this.#tail = node
        }
        this.#size++;
    }

    dequeue() {
        if (this.#size === 0) {
            return null;
        }
        const ret = this.#head!.data;
        this.#head = this.#head!.next
        // If this.#head.next is null, that means we've dequeued the only item in the queue
        // Therefore, if this.#head is null, queue is now empty and we need to update #tail accordingly
        if (this.#head === null) {
            this.#tail = null
        }
        this.#size--;
        return ret
    }

    peek() {
        return this.#size >= 1 ? this.#head!.data : null;
    }

    get size() { return this.#size; }
}

/**
 * Double-ended queue.
 * 
 * Live range is [#frontIndex, #backIndex)
 * 
 * Items is a Record rather than T[] so reindexing on appendleft is not required.
 */
export class Deque<T> {
    #backIndex;
    #frontIndex;
    items: Record<number, T>;

    constructor(items?: T[]) {
        this.items = {};
        this.#frontIndex = 0;
        this.#backIndex = 0;
        items?.forEach(i => this.append(i));
    }

    *[Symbol.iterator]() {
        for (let i = this.#frontIndex; i < this.#backIndex; i++) {
            yield this.items[i]!;
        }
    }

    appendleft(element: T) {
        this.#frontIndex--;
        this.items[this.#frontIndex] = element;
    }

    append(element: T) {
        this.items[this.#backIndex] = element;
        this.#backIndex++;
    }

    /** @returns null if the deque is empty */
    popleft(): T | null {
        if (this.isEmpty()) return null;
        const item = this.items[this.#frontIndex];
        delete this.items[this.#frontIndex];
        this.#frontIndex++;
        return item ?? null;
    }

    /** @returns null if the deque is empty */
    pop(): T | null {
        if (this.isEmpty()) return null;
        this.#backIndex--;
        const item = this.items[this.#backIndex];
        delete this.items[this.#backIndex];
        return item ?? null;
    }

    /** @returns null if the deque is empty */
    peekFront(): T | null {
        if (this.isEmpty()) return null;
        return this.items[this.#frontIndex] ?? null;
    }

    /** @returns null if the deque is empty */
    peekBack(): T | null {
        if (this.isEmpty()) return null;
        return this.items[this.#backIndex - 1] ?? null;
    }

    isEmpty() {
        return this.size === 0;
    }

    get size() {
        return this.#backIndex - this.#frontIndex;
    }

    clear() {
        this.items = {};
        this.#frontIndex = 0;
        this.#backIndex = 0;
    }
}