
import { isoDaysAgo, isoToUserDate } from '../shared/datetime';
import { initTimeEntryForm } from '../shared/forms';
import { api } from '../shared/services/api';
import { contextMenu } from '../shared/ui/context-menu';
import { handleDelete, openModalForEdit } from '../shared/ui/modal-manager';
import { required } from '../shared/utils';
import { FormDialog, TimeEntry } from '../types';
import type { PieDatum } from './chart';
import { TimeEntriesChart } from './chart';
import type { StatsEntry } from './stats';
import { deriveStatsView, toStatsShape, totalsBy } from './stats';

/**
 * Thoughts:
 * - Am I spending time on the right things?
 * - Balance: Am I over-indexing on one category and neglecting others?
 * - Work vs rest ratio: Burning out? Coasting?
 * - Trends: Is activity A going up or down over the given window?
 */


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
                        modal.querySelector('#pillar_ids_hidden').value = data.pillars.map(p => p.id).join(',') ?? '';
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

function getRenderStatsEls() {
    return {
        totalLabel: required(document.querySelector('.js-stat-total'), '.js-stat-total'),
        avgLabel: required(document.querySelector('.js-stat-daily-avg'), '.js-stat-daily-avg'),
        activeDaysLabel: required(document.querySelector('.js-stat-daily-avg-across-n-days'), '.js-stat-daily-avg-across-n-days'),
        topCategory: required(document.querySelector('.js-stat-top-cat'), '.js-stat-top-cat'),
        topCatLabel: required(document.querySelector('.js-stat-top-cat-time'), '.js-stat-top-cat-time'),
        mostActiveDay: required(document.querySelector('.js-stat-most-active-day'), '.js-stat-most-active-day'),
        totalDelta: required(document.querySelector('.js-stat-total-comparison'), '.js-stat-total-comparison'),
        mostActiveTime: required(document.querySelector('.js-stat-most-active-day-time'), '.js-stat-most-active-day-time'),
    }
}

function renderStats(vm: ReturnType<typeof deriveStatsView>) {
    const renderStatsEls = getRenderStatsEls();
    renderStatsEls.totalLabel.textContent = vm.totalLabel;
    renderStatsEls.avgLabel.textContent = vm.avgLabel;
    renderStatsEls.activeDaysLabel.textContent = vm.activeDaysLabel;
    renderStatsEls.topCategory.textContent = vm.topCategory;

    renderStatsEls.topCatLabel.textContent = vm.topCatLabel;
    renderStatsEls.mostActiveDay.textContent = vm.mostActiveDay;
    renderStatsEls.mostActiveTime.textContent = vm.mostActiveLabel;
    renderStatsEls.totalDelta.textContent = vm.totalDelta;
}


async function fetchEntries(range: number): Promise<TimeEntry[]> {
    const params = new URLSearchParams({ lastNDays: range.toString() })
    const response = await api.time_entries.summary(params)
    return response.data;
}

function toPieData(entries: StatsEntry[]): PieDatum[] {
    const totals = totalsBy(entries, e => e.category);
    return Object.entries(totals).map(([category, value]) => ({ category, value }));
}

class TimeTrackingDashboard {
    #chart: TimeEntriesChart;
    #range = 7;

    async loadRange(range: number) {
        const raw = await fetchEntries(range * 2);
        const entries = raw.map(toStatsShape);
        const cutoff = isoDaysAgo(range);
        const current = entries.filter(e => e.date >= cutoff);
        const prior = entries.filter(e => e.date < cutoff);
        renderStats(deriveStatsView(current, prior));
        this.#chart.updatePieChart(toPieData(current));
        // TODO: renderTable/List(entries)
    }

    async init() {
        this.#chart = new TimeEntriesChart('#time_tracking-chart-container');
        this.#setupRangeButtons();
        this.#syncActiveButton();
        await this.loadRange(this.#range);
    }

    #setupRangeButtons() {
        const pillsContainer = required(document.querySelector('.timeframe-selector'), '.timeframe-selector');
        pillsContainer.addEventListener('click', (e) => {
            const btn = e.target.closest<HTMLButtonElement>('[data-range]');
            if (!btn) return;
            const range = Number(btn.dataset.range);
            this.#range = range;
            this.#syncActiveButton();
            this.loadRange(range);
        })
    }
    #syncActiveButton() {
        document.querySelectorAll('[data-range]').forEach(pill => 
            pill.classList.toggle('active', Number(pill.dataset.range) === this.#range)
        );
    }
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

