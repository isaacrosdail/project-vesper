import type { HabitOverviewItemRead } from "../apiTypes";



export function targetDesc(h: HabitOverviewItemRead): string {
    const unit = h.type === 'duration' ? 'min' : (h.units ?? '');
    const t = h.target;
    if (!t || t.low === null && t.high === null) return unit;

    const range =
        t.kind === 'at_least' ? `${t.low}+`
        : t.kind === 'at_most' ? `≤${t.high}`
        : `${t.low}-${t.high}`;
    return `${range}${unit ? ' ' + unit : ''}/day`;
}
