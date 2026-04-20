import { confirmationManager } from './shared/ui/modal-manager';
import { makeToast } from './shared/ui/toast';
import { initPasswordToggles } from './shared/forms';

export function init() {
    initPasswordToggles();

    document.addEventListener('click', (e) => {
        const target = e.target as HTMLElement;
        if (target.matches('#default')) {
            confirmationManager.show("Are you sure?");
        }
        else if (target.matches('#toast-success')) {
            makeToast('Success: Thing worked', 'success');
        }
        else if (target.matches('#toast-error')) {
            makeToast('Error: Uh-oh, there was a problem', 'error')
        }
    });

    const gridContainer = document.querySelector('.component-catalog');
    // Since cards are static (not adding/removing cards here), we'll cache this:
    const allCards = gridContainer.querySelectorAll('.card-dashboard');
    let draggedCard;
    let draggedNextSibling;
    gridContainer.addEventListener('dragstart', (e) => {
        draggedCard = e.target.closest('.card-dashboard');
        draggedNextSibling = draggedCard.nextSibling;
    })
    gridContainer.addEventListener('dragover', (e) => {
        // without this, the browser just ignores the drop entirely weird quirk but
        e.preventDefault();
        allCards.forEach(c => c.classList.remove('dragover-target'));
        const draggingOverCard = e.target.closest('.card-dashboard');
        // highlight the card we 'would' place it on if we dropped it?
        if (draggingOverCard && draggingOverCard !== draggedCard) {
            draggingOverCard.classList.add('dragover-target')
        }
    })
    gridContainer.addEventListener('drop', (e) => {
        const overCard = e.target.closest('.card-dashboard');

        // Technique for transitions for this movement: 'FLIP'

        // Transition effect:
        // 1. FIRST: stash positions before swap
        const overCardRectBefore = overCard.getBoundingClientRect();
        const draggedCardRectBefore = draggedCard.getBoundingClientRect();

        // 2. LAST: Do the DOM swap then get bounding client rect on each again

        // A. DOM Swap
        // insertBefore to swap in DOM, grid reflows automatically
        // put dragged where target position's card was
        overCard.before(draggedCard)
        // put target position's card where dragged card's was:
        draggedNextSibling.before(overCard)

        // B. Get new positions for each
        const overCardRectAfter = overCard.getBoundingClientRect();
        const draggedCardRectAfter = draggedCard.getBoundingClientRect();

        // 3. INVERT: Calculate the difference (old pos minus new pos)
        const overCardDiffX = overCardRectBefore.x - overCardRectAfter.x;
        const overCardDiffY = overCardRectBefore.y - overCardRectAfter.y;
        const draggedCardDiffX = draggedCardRectBefore.x - draggedCardRectAfter.x;
        const draggedCardDiffY = draggedCardRectBefore.y - draggedCardRectAfter.y;

        // B. Apply that difference as a transform: this visually snaps them BACK to where they
        // were, even tho the DOM has already moved
        overCard.style.transform = `translate(${overCardDiffX}px, ${overCardDiffY}px)`
        draggedCard.style.transform = `translate(${draggedCardDiffX}px, ${draggedCardDiffY}px)`

        // C. Then remove the transform with a transition: The cards then animate from
        // their old visual position to their new DOM position
        requestAnimationFrame(() => {
            overCard.style.transition = 'transform 0.3s ease';
            overCard.style.transform = '';
            draggedCard.style.transition = 'transform 0.3s ease';
            draggedCard.style.transform = '';
        })

        // Reset outlines
        allCards.forEach(c => c.classList.remove('dragover-target'));
    })
}