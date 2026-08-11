

type PageSlot = { kind: 'page' | 'ellipsis'; num: number; };
export function paginationSlots(current: number, total: number, maxSlots: number): PageSlot[] {
    if (maxSlots % 2 === 0) {
        throw new Error('maxSlots value must be odd');
    }
    const lastPage = total - 1;
    const result: PageSlot[] = [];

    // // Render all
    if (total <= maxSlots) {
        for (let i = 0; i < total; i++) {
            result.push({ kind: 'page', num: i });
        }
        // run length W  = maxSlots - 2 (accounts for far anchor and the ellipsis slot)
        // +1 = accoutns for inclusive (6-4 alone gives 2, but that's 3 slots)
        // Right-anchored case: p >= lastPage - W + 1  <= 1 for inclusion
        //        W is our run ie how many slots in a row to render numbered
        // Left-anchored  case: p <= lastPage - W + 1
        //
    } else {
        const wEdge = maxSlots - 2; // left/right-anchored
        const wMid = maxSlots - 4; // centered case
        // Left-anchored: 1 2 3 ... 6
        if (current <= wEdge - 1) {
            for (let i = 0; i <= wEdge - 1; i++) {
                result.push({ kind: 'page', num: i });
            }
            result.push({ kind: 'ellipsis', num: wEdge - 1 });
            result.push({ kind: 'page', num: lastPage });
            // Right-anchored: 1 ... 4 5 6
        } else if (current >= lastPage - wEdge + 1) {
            result.push({ kind: 'page', num: 0 });
            result.push({ kind: 'ellipsis', num: lastPage - wEdge });
            for (let i = lastPage - wEdge + 1; i <= lastPage; i++) {
                result.push({ kind: 'page', num: i });
            }
        } else {
            // centered:
            // 0, ..., run centered on p, ..., lastPage
            const radius = (wMid - 1) / 2;
            result.push({ kind: 'page', num: 0 });
            result.push({ kind: 'ellipsis', num: current - radius - 1 });
            for (let i = current - radius; i <= current + radius; i++) {
                // wMid = 3
                // i needs to start @ 4
                // center - wMid? or center - wMid / 2?
                // start @ 4, end @ 6
                result.push({ kind: 'page', num: i });
            }
            result.push({ kind: 'ellipsis', num: current - radius + 1 });
            result.push({ kind: 'page', num: lastPage });
        }
    }
    return result;
}