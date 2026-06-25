
import { hourMinsDisplay } from '../shared/charts';
import { displayDate, formatToUserTimeString, isoDaysAgo, isoToUserDate, rangeLabel } from '../shared/datetime';
import { initTimeEntryForm } from '../shared/forms';
import { api } from '../shared/services/api';
import { sortByField } from '../shared/tables';
import { contextMenu } from '../shared/ui/context-menu';
import { handleDelete, openModalForEdit } from '../shared/ui/modal-manager';
import { required } from '../shared/utils';
import { FormDialog, TimeEntry } from '../types';
import type { PieDatum } from './chart';
import { TimeEntriesChart } from './chart';
import type { StatsEntry, StatsView } from './stats';
import { deriveStatsView, toStatsShape, totalsBy } from './stats';


type PageSlot = { kind: 'page' | 'ellipsis'; page: number; };

type SortState = {
    field: SortField;
    order: 'asc' | 'desc';
}
type SortField = typeof SORT_FIELDS[number];
const SORT_FIELDS = ['started_at', 'category', 'duration_minutes', 'description'] as const;
function isSortField(s: string): s is SortField {
    return (SORT_FIELDS.includes(s as SortField));
}


class TimeTrackingDashboard {
    #chart: TimeEntriesChart;
    #range = 7;
    #pageSize = 10;
    #page = 0;
    #currentRaw: TimeEntry[] = [];
    #sortState: SortState = { field: 'started_at', order: 'asc' };

    async loadRange(range: number) {
        const raw = await fetchEntries(range * 2);
        const entries = raw.map(toStatsShape);
        const cutoff = isoDaysAgo(range);
        this.#currentRaw = raw.filter(e => e.started_at.split('T')[0] >= cutoff);
        const current = entries.filter(e => e.date >= cutoff);
        const prior = entries.filter(e => e.date < cutoff);
        renderStats(deriveStatsView(current, prior));
        this.#chart.updatePieChart(toPieData(current));

        // update label:
        const prefix = range === 7 ? 'This week' : `Last ${range} days`;
        const header = required(document.querySelector('.page-h2'), '.page-h2');
        header.textContent = prefix;
        const timeFrameLabel = required(document.querySelector('.timeframe-label'), '.timeframe-label');
        timeFrameLabel.textContent = rangeLabel(range);

        this.#page = 0;
        this.#renderTable();
    }

    async init() {
        this.#chart = new TimeEntriesChart('#time_tracking-chart-container');
        this.#setupRangeButtons();
        this.#setupPaginationButtons();
        this.#setupSortingHeaders();
        this.#syncActiveButton();
        await this.loadRange(this.#range);
    }

    #setupSortingHeaders() {
        const table = required(document.querySelector('#time_entries-table'), '#time_entries-table');
        table.addEventListener('click', (e) => {
            const th = (e.target as HTMLElement).closest<HTMLTableCellElement>('th');
            if (!th?.dataset.column) return;
            const field = th.dataset.column;
            if (!field || !isSortField(field)) return;

            this.#sortState.order = field === this.#sortState.field
                ? (this.#sortState.order === 'desc' ? 'asc' : 'desc')
                : 'asc';
            // Apply sort dir state to DOM
            table.querySelector('th[data-order]')?.removeAttribute('data-order');
            th.dataset.order = this.#sortState.order;
            this.#sortState.field = field;
            this.#currentRaw = sortByField(this.#currentRaw, field, this.#sortState.order);
            this.#page = 0;
            this.#renderTable();
        })
    }
    #setupRangeButtons() {
        const pillsContainer = required(document.querySelector('.timeframe-selector'), '.timeframe-selector');
        pillsContainer.addEventListener('click', (e) => {
            const target = e.target as HTMLElement;
            const btn = target.closest<HTMLButtonElement>('[data-range]');
            if (!btn) return;
            const range = Number(btn.dataset.range);
            this.#range = range;
            this.#syncActiveButton();
            this.loadRange(range);
        })
    }
    #setupPaginationButtons() {
        const paginationControls = required(document.querySelector('.pagination-controls'), '.pagination-controls');
        paginationControls.addEventListener('click', (e) => {
            const btn = (e.target as HTMLElement).closest<HTMLButtonElement>('[data-pagination-page], [data-delta]');
            if (!btn) return;
            const target = btn.dataset.paginationPage !== undefined
                ? Number(btn.dataset.paginationPage)
                : this.#page + Number(btn.dataset.delta);
            this.#goToPage(target);
        })
    }
    #renderPagination() {
        const MAX_SLOTS = 7;
        // Redraw the number strip and mark active page
        const pageButtons = required(document.querySelector<HTMLElement>('.page-buttons'), '.page-buttons');
        // Append siblings for each page
        const myBtns = paginationSlots(this.#page, this.#lastPage, MAX_SLOTS).map(slot =>
            slot.kind === 'page'
                ? makePageBtn(slot.page, this.#page)
                : makeEllipsisBtn(slot.page)
        );
        pageButtons.replaceChildren(...myBtns);

        // Show count underneath
        const countLabel = required(document.querySelector('.count'), '.count');
        const total = this.#currentRaw.length;
        const start = this.#page * this.#pageSize;
        const from = total === 0 ? 0 : start + 1;
        const to = Math.min(start + this.#pageSize, total);
        countLabel.textContent = `${from}-${to} of ${total}`;

        // Disable back on first page, next on last
        const backBtn = required(document.querySelector<HTMLButtonElement>('.back'), '.back');
        const nextBtn = required(document.querySelector<HTMLButtonElement>('.next'), '.next');
        backBtn.disabled = this.#page === 0;
        nextBtn.disabled = this.#page === this.#lastPage;
    }
    get #lastPage() {
        return Math.max(0, Math.ceil(this.#currentRaw.length / this.#pageSize) - 1);
    }
    #goToPage(p: number) {
        this.#page = Math.min(Math.max(p, 0), this.#lastPage); // clamp to [0, lastPage]
        this.#renderTable();
    }
    #renderTable() {
        const tbody = required(document.querySelector('.mytbody'), '.mytbody');
        const start = this.#page * this.#pageSize;
        const slice = this.#currentRaw.slice(start, start + this.#pageSize);
        tbody.replaceChildren(...slice.map(buildTimeRow));
        this.#renderPagination();
    }
    #syncActiveButton() {
        document.querySelectorAll('[data-range]').forEach(pill => 
            pill.classList.toggle('active', Number(pill.dataset.range) === this.#range)
        );
    }
}


function paginationSlots(page: number, lastPage: number, maxSlots: number): PageSlot[] {
    const result: PageSlot[] = [];
    // Render all
    if (lastPage + 1 <= maxSlots) {
        for (let i = 0; i <= lastPage; i++) {
            result.push({ kind: 'page', page: i });
        }
    // Windowed
    } else {
        // [first] [...] [ ...window... ] [...] [last]
        //   1      ...       4 5 6        ...    30
        // then the window part would be maxSlots - 2 -> the "center" els of those?
        // So with odd maxSlots of 7:
        // That leaves 5 slots -> this.#page +/- TWO?
        // k = (5-2) / 2 -> 3/2 -> 1
        const k = Math.floor((maxSlots - 2) / 2);

        // So we really have ~3 cases within this right?
        // 1. Left-side anchored:               1 2 3 ... 6
        // 2. Right-side anchored:              1 ... 4 5 6
        // 3. Actually "anchored at this.page": 1 ... 4 ... 6
        let [windowLeft, windowRight] = [0, 0];
        // Right-anchored
        if (page >= lastPage - (k + 1)) {
            [windowLeft, windowRight] = [lastPage - (k+1), lastPage];
            result.push({ kind: 'page', page: 0 });
            result.push({ kind: 'ellipsis', page: windowLeft - 1 });
            for (let i = windowLeft; i <= windowRight; i++) {
                result.push({ kind: 'page', page: i });
            }

        // Left-anchored
        } else if (page <= k + 1) {
            [windowLeft, windowRight] = [0, 1 + k];
            for (let i = windowLeft; i <= windowRight; i++) {
                result.push({ kind: 'page', page: i });
            }
            result.push({ kind: 'ellipsis', page: windowRight + 1 });
            result.push({ kind: 'page', page: lastPage });

        // this.page-anchored
        } else {
            const remainingSlots = maxSlots - 4;
            const half = Math.floor(remainingSlots / 2);
            [windowLeft, windowRight] = [page - half, page + half];
            result.push({ kind: 'page', page: 0 });
            result.push({ kind: 'ellipsis', page: windowLeft - 1 });
            for (let i = windowLeft; i <= windowRight; i++) {
                result.push({ kind: 'page', page: i });
            }
            result.push({ kind: 'ellipsis', page: windowRight + 1 });
            result.push({ kind: 'page', page: lastPage });
        }
    }
    return result;
}

function buildTimeRow(entry: TimeEntry): HTMLTableRowElement {
    const rowTemplate = required(document.querySelector<HTMLTemplateElement>('#time-row-template'), '#time-row-template');
    const clone = rowTemplate.content.cloneNode(true) as DocumentFragment;
    const row = required(clone.querySelector('tr'), 'tr');

    row.querySelector('.date')!.textContent = displayDate(entry.started_at);
    row.querySelector('.category')!.textContent = entry.category;
    row.querySelector('.time')!.textContent = getTimeWindowLabel(entry)
    row.querySelector('.duration_minutes')!.textContent = hourMinsDisplay(entry.duration_minutes);
    row.querySelector('.description')!.textContent = entry.description ?? '';

    row.dataset.itemId = String(entry.id);

    return row;
}

function getTimeWindowLabel(entry: TimeEntry) {
    const start = formatToUserTimeString(new Date(entry.started_at));
    const end = formatToUserTimeString(new Date(entry.ended_at));
    return `${start} - ${end}`;
}

function makePageBtn(num: number, curr: number): HTMLButtonElement {
    const btn = document.createElement('button');
    btn.textContent = String(num+1)
    btn.classList.add('btn', 'btn-ghost');
    btn.dataset.paginationPage = String(num);
    if (num === curr) btn.classList.add('active');
    return btn;
}
const makeEllipsisBtn = (toPage: number) => {
    const btn = document.createElement('button');
    btn.textContent = '...';
    btn.classList.add('btn', 'btn-ghost');
    btn.dataset.paginationPage = String(toPage);
    return btn;
}


function setStat(key: string, value: string, detail: string, signal?: number) {
    const el = required(document.querySelector(`#${key}`), `#${key}`);
    const statsValueEl = required(el.querySelector('.stats-value'), '.stats-value');
    statsValueEl.textContent = value;
    const detailEl = el.querySelector('.stats-detail');
    if (detailEl) detailEl.textContent = detail;
    if (signal !== undefined) {
        el.querySelector<HTMLElement>('.signal')?.style.setProperty('--p', String(signal));
    }
}

function renderStats(vm: StatsView) {
    for (const [id, card] of Object.entries(vm)) {
        setStat(id, card.value, card.detail, card.statProgress)
    }
}


// TODO: We should grabt the largest window (90) _once_ on page load, cache it,
/// and then simply .filter for subset ranges (7/30/etc)
async function fetchEntries(range: number): Promise<TimeEntry[]> {
    const params = new URLSearchParams({ lastNDays: range.toString() })
    const response = await api.time_entries.summary(params)
    return response.data;
}

function toPieData(entries: StatsEntry[]): PieDatum[] {
    const totals = totalsBy(entries, e => e.category);
    return Object.entries(totals).map(([category, value]) => ({ category, value }));
}

function setupContextMenu() {
    document.addEventListener('click', async (e) => {
        const target = e.target as HTMLElement;
        // Handle table ellipsis options click
        if (!(target.matches('.js-table-options'))) {
            return
        }
        const button = target.closest('.row-actions')!;
        const row = target.closest<HTMLTableRowElement>('tr')!;
        const { itemId, subtype } = row.dataset;
        const modal = document.querySelector<FormDialog>('#time_entries-entry-dashboard-modal');
        const rect = button.getBoundingClientRect();

        contextMenu.create({
            position: { x: rect.left, y: rect.bottom },
            items: [
                {
                    label: 'Edit',
                    action: () => openModalForEdit<TimeEntry>(itemId, modal, 'Time Entry', (data) => {
                        const entryDateInput = modal.querySelector<HTMLInputElement>('#entry_date');
                        if (entryDateInput) {
                            entryDateInput.value = isoToUserDate(data.started_at);
                        }
                        // TODO: sync checkboxes for Pillars
                        data.pillars.forEach((p: {id: number}) => {
                            const cb = modal.querySelector(`input[value="${p.id}"]`);
                            if (cb) cb.checked = true;
                        })
                        // also sync the hidden input
                        modal.querySelector('#pillar_ids_hidden').value = data.pillars.map(p => p.id).join(',');
                    })
                },
                {
                    label: 'Delete',
                    action: () => handleDelete(itemId, subtype)
                }
            ]
        })
    });
}


export async function init() {
    // Pipeline: fetch -> TimeEntry[] -> .map(toStatsShape)
    //     -> StatsEntry[] -> deriveStatsView -> renderStats 
    await new TimeTrackingDashboard().init();

    const dialog = required(
        document.querySelector<FormDialog>('#time_entries-entry-dashboard-modal'),
        '#time_entries-entry-dashboard-modal'
    )
    initTimeEntryForm(dialog)

    setupContextMenu();
}

