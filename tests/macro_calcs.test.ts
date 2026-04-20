import { describe, test, expect } from 'bun:test';
import { pctToGrams, gramsToPct } from '../app/static_src/js/shared/ui/profile-sidebar';
import { calculateBMR } from '../app/static_src/js/shared/utils';

describe('pctToGrams', () => {
    test('protein 30% of 2000 cal', () => {
        expect(pctToGrams(2000, 30, 'protein_target')).toBe(150); // 2000 * 0.3 /
4
    });
    test('fat 30% of 2000 cal', () => {
        expect(pctToGrams(2000, 30, 'fat_target')).toBe(67); // 2000 * 0.3 / 9
    });
    test('carbs 40% of 2000 cal', () => {
        expect(pctToGrams(2000, 40, 'carbs_target')).toBe(200); // 2000 * 0.4 / 4
    });
    test('zero percent returns 0', () => {
        expect(pctToGrams(2000, 0, 'protein_target')).toBe(0);
    });
});

describe('gramsToPct', () => {
    test('150g protein of 2000 cal', () => {
        expect(gramsToPct(2000, 150, 'protein_target')).toBe(30); // 150 * 4 /
2000 * 100
    });
    test('67g fat of 2000 cal', () => {
        expect(gramsToPct(2000, 67, 'fat_target')).toBe(30); // 67 * 9 / 2000 *
100
    });
    test('roundtrip: pct -> grams -> pct', () => {
        const grams = pctToGrams(2200, 35, 'protein_target');
        const pct = gramsToPct(2200, grams, 'protein_target');
        expect(pct).toBe(35);
    });
});

describe('calculateBMR', () => {
    test('male BMR', () => {
        // 10 * 80 + 6.25 * 180 - 5 * 30 + 5 = 1780
        const bmr = calculateBMR('m', 80, 180, 1996, 2026);
        expect(bmr).toBe(1780);
    });
    test('female BMR', () => {
        // 10 * 60 + 6.25 * 165 - 5 * 25 - 161 = 1370.25
        const bmr = calculateBMR('f', 60, 165, 2001, 2026);
        expect(bmr).toBe(1345.25);
    });
});
