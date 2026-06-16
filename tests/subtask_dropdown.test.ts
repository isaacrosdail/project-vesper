import { describe, test, expect } from 'bun:test';
import { visibleSubtaskIds, type SubtaskDropdownState} from
'../app/static_src/js/tasks/subtask_dropdown';

function makeState(overrides: Partial<SubtaskDropdownState> = {}): SubtaskDropdownState {
    return {
        tasks: [{ id: 1, name: 'one' }, { id: 2, name: 'two' }, { id: 3, name: 'three' } ],
        selectedIds: new Set<number>(),
        excludeId: null,
        searchTerm: '',
        ...overrides,
    };
}

describe('visibleSubtaskIds', () => {
    test('returns all tasks when nothing is selected, excl, or searched', () => {
        const result = visibleSubtaskIds(makeState());
        expect(result).toEqual(new Set([1,2,3]));
    });
    test('excluded task stays hidden even when its name matches search', () => {
        const result = visibleSubtaskIds(makeState({ excludeId: 1, searchTerm: 'one' }));
        expect(result.has(1)).toBe(false);
    });
    test('selected task is hidden', () => {
        const result = visibleSubtaskIds(makeState({ selectedIds: new Set([3]) }));
        expect(result).toEqual(new Set([1, 2]));
    });
    test('search filters non-matches', () => {
        const result = visibleSubtaskIds(makeState({ searchTerm: 'one' }));
        expect(result).toEqual(new Set([1]));
    });
    test('search is case insensitive and trims whitespace', () => {
        const result = visibleSubtaskIds(makeState({ searchTerm: '  THREe  ' }));
        expect(result).toEqual(new Set([3]));
    });
    test('empty task list results in empty set', () => {
        const result = visibleSubtaskIds(makeState({ tasks: [] }));
        expect(result).toEqual(new Set());
    })
})
