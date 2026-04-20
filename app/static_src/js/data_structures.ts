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

export class Queue<T> {
    head: QueueNode<T> | null;
    tail: QueueNode<T> | null;
    size: number;

    constructor() {
        this.head = null
        this.tail = null
        this.size = 0
    }

    enqueue(val: T) {
        const node = new QueueNode(val)
        if (this.size === 0) {
            this.head = node
            this.tail = node
        } else {
            // link old tail to it
            this.tail!.next = node
            this.tail = node
        }
        this.size++;
    }

    dequeue() {
        if (this.size === 0) {
            return null;
        }
        const ret = this.head!.data;
        this.head = this.head!.next
        // If this.head.next is null, that means we've dequeued the only item in the queue
        // Therefore, if this.head is null, queue is now empty and we need to update tail accordingly
        if (this.head === null) {
            this.tail = null
        }
        this.size--;
        return ret
    }

    peek() {
        return this.size >= 1 ? this.head!.data : null;
    }
}