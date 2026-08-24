import type { Action } from "svelte/action";

const CARD = '.card-dashboard';

function cardFrom(target: EventTarget | null): HTMLElement | null {
    return target instanceof Element ? target.closest<HTMLElement>(CARD) : null;
}

export const dragReorder: Action<HTMLElement> = (node) => {
    // Since cards are static (not adding/removing cards here), we'll cache this:
    const allCards = node.querySelectorAll('.card-dashboard');
    let draggedCard: HTMLElement;
    let draggedNextSibling: HTMLElement;

    function onDragStart(e: DragEvent) {
        draggedCard = cardFrom(e.target);
        draggedNextSibling = draggedCard.nextSibling;
    }
    function onDragOver(e: DragEvent) {
        // without this, the browser just ignores the drop entirely weird quirk but
        e.preventDefault();
        allCards.forEach(c => c.classList.remove('dragover-target'));
        const draggingOverCard = cardFrom(e.target);
        // highlight the card we 'would' place it on if we dropped it?
        if (draggingOverCard && draggingOverCard !== draggedCard) {
            draggingOverCard.classList.add('dragover-target')
        }
    }
    function onDragEnd(e: DragEvent) {
        allCards.forEach(c => c.classList.remove('dragover-target'));
    }
    function onDrop(e: DragEvent) {
        const overCard = cardFrom(e.target);

        // Technique for transitions for this movement: 'FLIP'
        // 1. First: Stash where things are pre-swap
        // 2. Last: Swap, then get where they are now
        // 3. Invert: Transform by (First - Last), so they render in their old spots.
        //  This step has to be instant.
        // 4. Play: Drop the transform with a transition -> they animate back into their real spots.

        // 1. FIRST: stash positions before swap
        const overCardRectBefore = overCard.getBoundingClientRect();
        const draggedCardRectBefore = draggedCard.getBoundingClientRect();

        // 2. LAST: Do the DOM swap then get bounding client rect on each again
        // A. DOM Swap: Put dragged where target position's card was
        // We use marker to stash our spot, since we otherwise can't move while referencing positions?
        // insertBefore to swap in DOM, grid reflows automatically
        const marker = document.createComment('');
        overCard.before(marker); // remember where 'overCard' sits
        draggedCard.before(overCard); // move 'overCard' to draggedCard's slot
        marker.replaceWith(draggedCard); // move dragged into the remembered slot

        // B. Get new positions for each
        const overCardRectAfter = overCard.getBoundingClientRect();
        const draggedCardRectAfter = draggedCard.getBoundingClientRect();

        // 3. INVERT
        // Sets transform from nothing to the offset
        //   This has to be instant: if it animates, the card visibly slides backward to where it used to be
        // Calculate the difference (old pos minus new pos)
        const overCardDiffX = overCardRectBefore.x - overCardRectAfter.x;
        const overCardDiffY = overCardRectBefore.y - overCardRectAfter.y;
        const draggedCardDiffX = draggedCardRectBefore.x - draggedCardRectAfter.x;
        const draggedCardDiffY = draggedCardRectBefore.y - draggedCardRectAfter.y;

        // B. Apply that difference as a transform: this visually snaps them BACK to where they
        // were, even tho the DOM has already moved
        for (const el of [overCard, draggedCard]) el.style.transition = 'none';
        overCard.style.transform = `translate(${overCardDiffX}px, ${overCardDiffY}px)`
        draggedCard.style.transform = `translate(${draggedCardDiffX}px, ${draggedCardDiffY}px)`

        // Force style flush by reading a layout property between Invert and Play:
        overCard.offsetHeight;

        // C. Then remove the transform with a transition: The cards then animate from
        // their old visual position to their new DOM position
        requestAnimationFrame(() => {
            for (const el of [overCard, draggedCard]) {
                el.style.transition = 'transform 0.3s ease';
                el.style.transform = '';
            }
        });
    };

    node.addEventListener('dragstart', onDragStart);
    node.addEventListener('dragover', onDragOver);
    node.addEventListener('dragend', onDragEnd);
    node.addEventListener('drop', onDrop);

    return {
        destroy() {
            // listener removal
            node.removeEventListener('dragstart', onDragStart);
            node.removeEventListener('dragover', onDragOver);
            node.removeEventListener('dragend', onDragEnd);
            node.removeEventListener('drop', onDrop);
        },
    };
};
