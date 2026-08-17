import { Queue, Deque } from "../dataStructures";

/// TODO:
// descendantSum for that "sum of estimates over task node and all its dependency subtasks"

/**
 * Kahn's algorithm for topological sort.
 * 
 * @returns topologically-sorted array of nodeIds, or null if there's a cycle.
 */
export function kahns(nodeIds: number[], edges: Array<[from: number, to: number]>): number[] | null {
    // 1. build in-degree count for every node
    const inDegree = new Map<number, number>();
    nodeIds.forEach(id => inDegree.set(id, 0));

    // Adjacency map: parent -> children
    // This turns later O(V*E) lookups into O(1)
    const adjMap = new Map<number, number[]>();
    edges.forEach(([from, to]) => {
        // Set in-degree counts for each:
        inDegree.set(to, inDegree.get(to)! + 1);

        // Build up adjacency map
        if (!adjMap.has(from)) {
            adjMap.set(from, [])
        }
        adjMap.get(from)!.push(to)
    })

    // 2. Collect all nodes with in-degree of 0 into queue
    const queue = new Queue<number>();
    inDegree.forEach((degree, nodeId) => {
        if (degree === 0) queue.enqueue(nodeId);
    });

    // 3. While queue isn't empty: pull a node, add to result, decrement in-degree of all its neighbors.
    // If any neighbor hits 0, add to queue.
    const result: number[] = []
    let nodeId: number | null;
    while ((nodeId = queue.dequeue()) !== null) {
        result.push(nodeId);

        // Decrement degree of all its neighbors: its children (subtasks) now have one fewer blocker?
        (adjMap.get(nodeId) ?? []).forEach(l => {
            inDegree.set(l, inDegree.get(l)! - 1); // decrement each one's inDegree in map
            if (inDegree.get(l) === 0) {
                queue.enqueue(l)
            }
        })
    }
    // Cycle
    if (result.length < nodeIds.length) {
        return null;
    }
    return result
}

/**
 * Finds every node reachable within `n` hops, keyed by node ID and valued by how many hops away it is.
 * 
 * @param adj Adjacency map of node to its neighbors
 * @param start Starting node, included in the result
 * @param n Number of hops, inclusive
 */
export function withinHops(adj: Map<number, Set<number>>, start: number, n: number = 1) {
    const dq = new Deque<number>([start]);
    const dist = new Map<number, number>([[start, 0]]);

    while (dq.size) {
        const curr = dq.popleft()!;
        const currDist = dist.get(curr)!;
        if (currDist === n) break;

        for (const neighbor of adj.get(curr) ?? []) {
            if (!dist.has(neighbor)) {
                dq.append(neighbor);
                dist.set(neighbor, currDist + 1);
            }
        }
    }
    return dist;
}