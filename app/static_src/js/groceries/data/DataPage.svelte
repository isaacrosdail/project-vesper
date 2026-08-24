
<script lang="ts">
    import { title } from '../../shared/formatters';
    import { storageAvailable } from '../../shared/dom';
    import { fmtDate, todayUser, userDay } from '../../shared/datetime';
    import Dropdown from '../../shared/components/Dropdown.svelte';
    import PaginatedTable from '../../shared/components/PaginatedTable.svelte';
    import { sortByField } from '../../shared/tables';
    import { Temporal } from 'temporal-polyfill';
    import type { ProductRead, TransactionRead } from '../../apiTypes';
    import { api } from '../../shared/services/api';
    import ProductForm from './ProductForm.svelte';
    import TransactionForm from './TransactionForm.svelte';

    // TODO(svelte):
    // 1. Missing: search, "Add entry", Inventory/Ledger tables, context menu
    // 2. CSV import button/functionality

    type TableOption = 'products' | 'transactions' | 'inventory' | 'ledger';
    type ColumnConfig = {
        label: string; // technically should prob be of type SORT_LABELS or something?
        key: string; // field name on the data
        format?: (value: unknown, row: unknown) => string; // optional function taking a val and rets a string
    }

    // TODO:
    // Loads default/initial load values based on user prefs
    // function loadDefaults() {
    //     // TODO: Now use local storage
    //     if (storageAvailable("localStorage")) {
    //         state.table = localStorage.getItem('defaultDataTable') || 'products';
    //         state.timeframe = Number(localStorage.getItem('defaultDataTimeframe')) || 30;

    //     } else {
    //         state.table = 'products';
    //         state.timeframe = 30;
    //     }
    //     // state.table = prefs.default_table || 'products';
    //     // state.timeframe = Number(prefs.default_timeframe) || 30;
    // }

    const configs: Record<TableOption, { cols: ColumnConfig[] }> = {
        products: {
            cols: [
                { label: 'Name', key: 'name' },
                { label: 'Category', key: 'category', format: (v) => `${title(v.replace('_', ' & '))}`},
                { label: 'Net Weight', key: 'net_weight', format: (v, row) => `${v} (${row.unit_type})`},
                { label: 'Calories', key: 'calories' },
            ]
        },
        transactions: {
            cols: [
                { label: 'Product', key: 'product_name'},
                { label: 'Price', key: 'price_at_scan', format: (v) => `$${v.toFixed(2)}`},
                { label: 'Price/100g', key: 'price_per_100g', format: (v) => `$${v.toFixed(2)}`},
                { label: 'Date', key: 'created_at', format: (v) => fmtDate(v) },
            ]
        }
    };

    const controls = $state({
        table: (localStorage.getItem('defaultDataTable') ?? 'products') as TableOption,
        timeframe: 7,
        search: '',
        sort: { order: 'asc', key: 'name' },
        pageSize: 10,
    });

    let cache = $state<{products: ProductRead[], transactions: TransactionRead[]}>({
        products: [], transactions: []
    });
    async function loadData() {
        const [productData, transactionData] = await Promise.all([
            api.products.getAll(), api.transactions.getAll()
        ]);
        cache.products = productData.data;
        cache.transactions = transactionData.data;
    }
    loadData();
    const filtered = $derived.by(() => {
        const cutoff = todayUser().subtract({ days: controls.timeframe });
        let rows = cache[controls.table].filter(r => Temporal.PlainDate.compare(userDay(r.created_at), cutoff) >= 0);
        if (controls.search) {
            const q = controls.search.toLowerCase();
            rows = rows.filter(r => cols.some(
                c => String(r[c.key] ?? '').toLowerCase().includes(q)));
        }
        return rows;
    });
    const sorted = $derived(controls.sort.order ? sortByField(filtered, controls.sort.key, controls.sort.order) : filtered);
</script>

<ProductForm />
<TransactionForm />


<section class="card-dashboard surface">
    <div class="table-controls">

        <input id="search-table" type="search" placeholder="Search table">
        <!-- enctype tells the browser to send the file as binary data rather than URL-encoded text -->
        <!-- <form method="POST" action="/groceries/nutrition_logs" enctype="multipart/form-data">
            <input type="hidden" name="csrf_token" value="{{ g.csrf_token }}">
            <input type="file" id="csv-file" name="file" accept=".csv" autocomplete="off" hidden>
            <button type="button" id="csv-import-btn" class="btn btn-secondary">
                Import CSV
            </button>
        </form> -->
        <!-- <button class="btn">CSV Import</button> -->
        <button data-add-btn class="btn btn-primary">+ Add Entry</button>

        <Dropdown label="Select Table"
            opts={[
                ['Products', 'products'], ['Transactions', 'transactions'],
                ['Inventory', 'inventory'], ['Ledger', 'ledger']
            ]}
            onSelect={(v) => controls.table = v} />

        <label>
            Timeframe:
            <input type="number" min="1" max="365" id="timeframe" bind:value={controls.timeframe}>
        </label>

      <Dropdown label="Page size"
          opts={[['10', '10'], ['25', '25'], ['50', '50'], ['100', '100']]}
          onSelect={(v) => controls.pageSize = Number(v)} />

    </div>

    <!-- {#key expr} destroys and recreates everything inside whenever the expr changes
        component remounts, page is born again at 0 
    -->
    {#key controls.table}
        <PaginatedTable items={sorted} pageSize={controls.pageSize} getKey={(r) => r.id}>
            <!-- SNIPPETS: -->
            {#snippet header()}
                <tr>
                    {#each configs[controls.table].cols as col (col.key)}
                        <!-- <th onclick={() => setSort(col.key)}></th> -->
                        <th onclick={() => console.log("implement me pls")}>{col.label}</th>
                    {/each}
                </tr>
            {/snippet}
            <!-- row is the snippet, 'r' is the parameter (ie each row 'formula'?) -->
            {#snippet row(r)}
                <tr oncontextmenu={() => console.log("nah")}>
                    {#each configs[controls.table].cols as col (col.key)}
                        <td>{col.format && r[col.key] != null ? col.format(r[col.key], r) : r[col.key] ?? ''}</td>
                    {/each}
                </tr>
            {/snippet}
        </PaginatedTable>
    {/key}

</section>


<style>
    .table-controls {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        align-items: center;
        gap: var(--space-sm);
        font-size: var(--font-size-sm);
    }
</style>