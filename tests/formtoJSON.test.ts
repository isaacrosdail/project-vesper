// tests/formToJSON.test.ts
import { describe, test, expect } from 'bun:test';
import { parseFormData } from '../app/static_src/js/shared/utils';

const cases = [
    { name: 'basic string', entries: [['name', 'Test']], expected: { name: 'Test' } },
    { name: 'empty string becomes null', entries: [['name', '']], expected: { name: null } },
    { name: 'checkbox on becomes true', entries: [['is_promotable', 'on']], expected: { is_promotable: true } },
    { name: 'array field parsed', entries: [['pillar_ids[]', '1,3,5']], expected: { pillar_ids: [1, 3, 5] } },
    { name: 'empty array field', entries: [['pillar_ids[]', '']], expected: { pillar_ids: [] } },
    { name: 'zero stays as string', entries: [['quantity', '0']], expected: { quantity: '0' } },
];

describe('parseFormData', () => {
    cases.forEach(({ name, entries, expected }) => {
        test(name, () => {
            const fd = new FormData();
            entries.forEach(([k, v]) => fd.append(k, v));
            expect(parseFormData(fd)).toEqual(expected);
        })
    })
});

