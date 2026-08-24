<script lang="ts">
    import FormModal from '../../shared/components/FormModal.svelte';
    import ProductFields, { emptyProductDraft, toProductPayload, type ProductDraft } from './ProductFields.svelte';
    import { api } from '../../shared/services/api';
    import { addToast } from '../../shared/components/Toaster.svelte';
    import type { ProductRead } from '../../apiTypes';

    let { onSuccess } = $props<{ onSuccess?: (product: ProductRead, isEdit: boolean) => void }>();

    let isOpen = $state(false);
    let editingId = $state<number | null>(null);
    let draft = $state<ProductDraft>(emptyProductDraft());

    export async function open(opts: { editId?: number } = {}) {
        editingId = opts.editId ?? null;
        if (editingId !== null) {
            const { data } = await api.products.getById(String(editingId));
            draft.name = data.name;
            draft.category = data.category;
            draft.barcode = data.barcode ?? '';
            draft.calories_per_100g = data.calories_per_100g != null ? String(data.calories_per_100g) : '';
            draft.net_weight = String(data.net_weight);
            draft.unit_type = data.unit_type;
        } else {
            draft = emptyProductDraft();
        }
        isOpen = true;
    }

    async function submit(e: SubmitEvent) {
        e.preventDefault();
        const payload = toProductPayload(draft);
        const isEdit = editingId !== null;
        const { data, message } = isEdit
            ? await api.products.patch(String(editingId), payload)
            : await api.products.post(payload);
        addToast(message, '', 'success');
        isOpen = false;
        onSuccess?.(data, isEdit);
    }
</script>

<FormModal title={editingId !== null ? 'Edit Product' : 'Add Product'} bind:open={isOpen}>
    <form class="form-column" onsubmit={submit}>
        <ProductFields product={draft} />
        <div class="form-actions">
            <button type="submit" class="btn btn-primary">Save</button>
        </div>
    </form>
</FormModal>