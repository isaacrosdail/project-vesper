

export type SubtaskDropdownState = {
    tasks: { id: number; name: string }[];
    selectedIds: Set<number>;
    excludeId: number | null;
    searchTerm: string;
};

export function visibleSubtaskIds(
    state: SubtaskDropdownState
): Set<number> {
    const term = state.searchTerm.trim().toLowerCase();
    return new Set(
        state.tasks
            .filter(t => !state.selectedIds.has(t.id)) // exclude tasks chosen (those are pills now)
            .filter(t => t.id !== state.excludeId) // exclude 'this' task (in edit mode)
            .filter(t => t.name.toLowerCase().includes(term)) // exclude those not matching search term
            .map(t => t.id)
    );
}
