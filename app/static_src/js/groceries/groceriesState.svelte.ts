import { api } from '../shared/services/api';
import type { ShoppingListItemRead, RecipeSlotRead } from '../apiTypes';
import type { MacrosSummaryRead } from "../apiTypes";

export const shoppingList = $state<{
    items: ShoppingListItemRead[];
    lastPrices: Record<number, number>;
}>({
    items: [],
    lastPrices: {},
});

export const kitchen = $state<{
    slots: RecipeSlotRead[];
    macros: MacrosSummaryRead | null;
}>({
    slots: [],
    macros: null,
});

export async function refreshShoppingList() {
    const { data } = await api.shopping_list.get(String(1));
    shoppingList.items = data;
}

export async function refreshSlots() {
    const { data } = await api.recipes.slots();
    kitchen.slots = data;
}

export async function refreshMacros() {
    const { data } = await api.macros.summary(new URLSearchParams({ lastNDays: String(1) }));
    kitchen.macros = data;
}

export const recipeForm = $state<{ open: boolean; editingId: number | null }>({
    open: false,
    editingId: null,
});

export function openRecipeForm(editingId: number | null = null) {
    recipeForm.editingId = editingId;
    recipeForm.open = true;
}
