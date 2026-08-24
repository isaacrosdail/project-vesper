<script lang="ts">
    import FormModal from '../../shared/components/FormModal.svelte';
    import ProductFields, { emptyProductDraft, toProductPayload, type ProductDraft } from './ProductFields.svelte';
    import { api } from '../../shared/services/api';
    import { addToast } from '../../shared/components/Toaster.svelte';
    import type { ProductRead, TransactionRead } from '../../apiTypes';
    import { priceMask } from './data';

    let { onSuccess } = $props<{ onSuccess?: (txn: TransactionRead, isEdit: boolean) => void }>();

    let isOpen = $state(false);
    let editingId = $state<number | null>(null);
    let products = $state<ProductRead[]>([]);

    function blankForm() {
        return {
            product_id: '',
            price_at_scan: '',
            quantity: '1',
        }
    };
    let form = $state(blankForm());
    let newProduct = $state<ProductDraft>(emptyProductDraft());

    const isNewProduct = $derived(form.product_id === '__new__');

    export async function open(opts: { editId?: number } = {}) {
        editingId = opts.editId ?? null;
        if (!products.length) api.products.getAll().then(({ data }) => products = data);
        if (editingId !== null) {
            const { data } = await api.transactions.getById(String(editingId));
            form.price_at_scan = data.price_at_scan.toFixed(2);
            form.quantity = String(data.quantity);
            form.product_id = String(data.product_id);   // display only; patch won't send it
        } else {
            form = blankForm();
            newProduct = emptyProductDraft();
        }
        isOpen = true;
    }

    async function submit(e: SubmitEvent) {
        e.preventDefault();
        const isEdit = editingId !== null;
        const base = { price_at_scan: form.price_at_scan, quantity: Number(form.quantity) };
        const { data, message } = isEdit
            ? await api.transactions.patch(String(editingId), base)
            : await api.transactions.post(
                isNewProduct
                    ? { ...base, product: toProductPayload(newProduct) }
                    : { ...base, product_id: Number(form.product_id) }
            );
        addToast(message, '', 'success');
        isOpen = false;
        onSuccess?.(data, isEdit);
    }
</script>

<FormModal title={editingId !== null ? 'Edit Transaction' : 'Add Transaction'} bind:open={isOpen}>
    <form class="form-column" onsubmit={submit}>
        <!-- Txn patch: -->
        {#if editingId === null}
            <div>
                <label for="txn-product">Product:</label>
                <select id="txn-product" bind:value={form.product_id} required>
                    <option value="">--</option>
                    <option value="__new__">+ New product</option>
                    {#each products as p (p.id)}<option value={String(p.id)}>{p.name}</option>{/each}
                </select>
            </div>
            {#if isNewProduct}
                <ProductFields product={newProduct} idPrefix="txn-product" />
            {/if}
        {/if}
        <div class="field-pair">
            <div>
                <label for="txn-price">Price:</label>
                <input id="txn-price" type="text" inputmode="decimal"
                    bind:value={form.price_at_scan} use:priceMask required>
            </div>
            <div>
                <label for="txn-qty">Quantity:</label>
                <input id="txn-qty" type="text" inputmode="numeric" bind:value={form.quantity} required>
            </div>
        </div>
        <div class="form-actions">
            <button type="submit" class="btn btn-primary">Save</button>
        </div>
    </form>
</FormModal>