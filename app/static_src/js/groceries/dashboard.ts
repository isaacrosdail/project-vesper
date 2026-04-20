import * as d3 from 'd3';
import { initProductForm, initTransactionForm } from '../shared/forms';
import { api } from '../shared/services/api';
import { makeToast } from '../shared/ui/toast';
import { FormDialog } from '../types';


function addShoppingListItemToDOM(itemId: string, productId: string, productName: string, detailStr: string, quantity = 1
) {
    const ul = document.querySelector('.shopping-list');
    if (!ul) {
        throw new Error('Shopping list <ul> not found')
    }

    // Clone the contents of our template for the new li
    const template = document.querySelector<HTMLTemplateElement>('#shopping-list-item-template');
    const fragment = template?.content.cloneNode(true) as DocumentFragment;
    const li = fragment.querySelector('li');
    if (!li) throw new Error('li not found in template');

    const itemName = li.querySelector('.item-name');
    const input = li.querySelector<HTMLInputElement>('input')
    const itemDetail = li.querySelector('.item-detail');
    if (!itemName || !input || !itemDetail) throw new Error('Template structure invalid');

    input.value = String(quantity);
    itemName.textContent = productName;
    itemDetail.textContent = detailStr;
    li.dataset['itemId'] = itemId;
    li.dataset['productId'] = productId;
    ul.appendChild(li);
}

// TODO: Needed here still?
/**
 * Adds product to shopping list or increments quantity if already present.
 */
async function handleAddToShoppingList(
    productId: string,
) {
    const response = await api.shopping_list.addItem(productId)
    const { id, product_id, product_name, unit_type, net_weight } = response.data;
    const existingLi = document.querySelector<HTMLLIElement>(`li[data-product-id="${productId}"]`);
    if (existingLi) {
        const input = existingLi.querySelector('input');
        const qty = input.value;
        const newQty = String(Number(qty) + 1);
        input.value = newQty
        makeToast(`Updated ${product_name} quantity to ${newQty}`, 'success');
        return;
    }

    const detailStr = `(${Math.round(net_weight)}${unit_type})`
    addShoppingListItemToDOM(id, product_id, product_name, detailStr);
    makeToast(`Added ${product_name} to shopping list`, 'success');
}

async function renderSparkline() {
    const response = await api.nutrition_log.summary(new URLSearchParams({ lastNDays: '10' }));
    const data = response.data.map(d => ({
        date: new Date(d.date),
        value: d.value
    }));
    const sparkline = d3.select('.sparkline-chart');
    const container = document.querySelector('.sparkline-chart')
    const width = container.clientWidth;
    const height = 40; // tiny

    const padding = 4;
    const x = d3.scaleTime().domain(d3.extent(data, d => d.date)).range([0, width]);
    const y = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.value)])
        .range([height - padding, 0]);

    const line = d3.line()
        .x(d => x(d.date))
        .y(d => y(d.value));

    sparkline.append('svg')
        .attr('width', '100%')
        .attr('height', height)
        .append('path')
        .datum(data)
        .attr('d', line)
        .attr('fill', 'none')
        .attr('stroke', 'var(--accent-strong)')
        .attr('stroke-width', 1.5);

    // TODO: clean this up, but also swap days and avg texts:
    const daysSpan = document.querySelector('.days');
    const avgSpan = document.querySelector('.avg');
    const avg = data.reduce((sum, curr) => sum + curr.value, 0) / data.length;
    daysSpan.textContent = `${data.length} days`;
    avgSpan.textContent = `avg: ${avg.toFixed(0)}kcal`;

    // remove "loading" effect w shimmer:
    [daysSpan, avgSpan]?.forEach(el => el.classList.remove('loading'))
}

export async function init() {
    await renderSparkline();

    // TODO: for the progbar
    const calsprog = document.querySelector('.calsprog');
    const progress = calsprog.dataset.prog
    calsprog.style.setProperty('--prog', 1 - (progress));

    // init forms - TODO: remove?
    const productFormDialog = document.querySelector<FormDialog>('#products-entry-dashboard-modal')
    if (!productFormDialog) {
        console.warn('groceries dashboard: #products-entry-dashboard-modal not found')
        return
    }
    initProductForm(productFormDialog)

    const transactionFormDialog = document.querySelector<FormDialog>('#transactions-entry-dashboard-modal')
    if (!transactionFormDialog) {
        console.warn('groceries dashboard: #transactions-entry-dashboard-modal not found')
        return
    }
    initTransactionForm(transactionFormDialog)

}
