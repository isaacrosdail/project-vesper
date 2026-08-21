/**
 * API client.
 * Ensures base URL prefix /api, CSRF/Auth headers, and body encoding.
 * 
 */

import type {
    DailyMetricsRead, DailyMetricsCreate, HabitRead, HabitCompletionCreate, HabitCreate, HabitPatch, MealEnum,
    ProductRead, ProductCreate, RecipeRead, RecipeCreate, ShoppingListItemRead, TaskRead, TaskCreate, TaskLink,
    TaskPatch, TimeEntryRead, TimeEntryCreate, TransactionRead, TransactionCreate, TransactionPatch,
    PillarRead, TaskStatRead,
    HabitOverviewItemRead,
    HabitCompletionProgressRead,
    HabitCompletionRead,
    MacrosSummaryRead,
    UserMeRead
} from '../../apiTypes';
import { nowISO, todayUser } from "../datetime";


// Top-level
type RequestData =
    | { [key: string]: JsonValue }
    | FormData
    | null;

// Inside obj
type JsonValue = 
    | string | number | boolean | null
    | { [key: string]: JsonValue }
    | JsonValue[];

type HTTPMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

type ApiSuccessResponse<T = unknown> = {
    success: true;
    message: string;
    data: T;
};

type ApiErrorResponse = {
    success: false;
    code: string;
    message: string;
    errors: Record<string, string[]> | null;
}

type ApiResponse<T> = ApiSuccessResponse<T> | ApiErrorResponse;

export class ApiError extends Error {
    code: string;
    status: number;
    errors: Record<string, string[]> | null;

    constructor(response: ApiErrorResponse, status: number) {
        super(response.message);
        this.code = response.code;
        this.status = status;
        this.errors = response.errors;
    }
}



class ApiClient {
    private async request<T = unknown>(
        method: HTTPMethod,
        path: string,
        data?: RequestData
    ): Promise<ApiSuccessResponse<T>> {
        if (!window.csrfToken) {
            throw new Error('CSRF token not found');
        }

        const isFormData = data instanceof FormData;
        const headers = new Headers({ 'X-CSRFToken': window.csrfToken });
        if (!isFormData) {
            headers.set('Content-Type', 'application/json');
        }

        const response = await fetch(`/api${path}`, {
            method,
            headers,
            body: isFormData ? data : (data ? JSON.stringify(data) : null),
        });

        let responseData: ApiResponse<T>;
        try {
            responseData = await response.json();
        } catch (err) {
            throw new ApiError({
                success: false,
                code: 'INVALID_RESPONSE',
                message: 'Server returned an unexpected response',
                errors: null
            }, response.status);
        }

        if (!responseData.success) {
            throw new ApiError(responseData as ApiErrorResponse, response.status);
        }
        return responseData;
    }

    private resource<T, TCreate, TPatch = Partial<TCreate>>(path: string) {
        return {
            getAll: (params?: URLSearchParams) => this.request<T[]>('GET', `${path}${params ? '?' + params : ''}`),
            getById: (id: string) => this.request<T>('GET', `${path}/${id}`),
            post: (data: TCreate) => this.request<T>('POST', path, data),
            // put: (id: string, data: any) => this.request('PUT', `${path}/${id}`, data),
            patch: (id: string, data: TPatch) => this.request<T>('PATCH', `${path}/${id}`, data),
            delete: (id: string) => this.request<T>('DELETE', `${path}/${id}`),
        };
    }

    tasks = {
        ...this.resource<TaskRead, TaskCreate, TaskPatch>('/tasks/tasks'),
        toggleComplete: (id: string, isDone: boolean) =>
            this.request<TaskPatch>('PATCH', `/tasks/tasks/${id}`, {
                completed_at: isDone ? nowISO() : null
            }),
        stats: () => this.request<{ overdue: TaskStatRead, frog: TaskStatRead }>('GET', '/tasks/stats')
    };

    taskLinks = {
        // TODO: Dbl check this one
        post: (data: TaskLink) => this.request<TaskRead>('POST', '/tasks/task_links', data) 
    }

    habits = {
        ...this.resource<HabitRead, HabitCreate, HabitPatch>('/habits/habits'),
        overview: () => this.request<{ habits: HabitOverviewItemRead[]; progress: HabitCompletionProgressRead }>('GET', '/habits/overview'),
    }

    habitCompletions = {
        post: (habitId: number, entryDate: string, value: number | null) => this.request<HabitCompletionRead>('POST', `/habits/${habitId}/completions`, {
            entry_date: entryDate,
            value,
        }),
        delete: (habitId: number, date: string) =>
            this.request('DELETE', `/habits/${habitId}/completions?date=${date}`),
        summary: (params: URLSearchParams) => this.request<BarData[]>('GET', `/habits/habit_completions/summary?${params}`),
        heatmap: (params?: URLSearchParams) => this.request<HeatmapApiEntry[]>('GET', `/habits/habit_completions/heatmap?${params ?? ''}`),
        get: (habitId: number, { start, end }: { start: string; end: string; }) => {
            const params = new URLSearchParams({ start, end });
            return this.request<HabitDayRead[]>('GET', `/habits/${habitId}/completions?${params}`);
        }
    }

    daily_metrics = {
        ...this.resource<DailyMetricsRead, DailyMetricsCreate>('/metrics/daily_metrics'),
        aggregate: (params: URLSearchParams) => this.request<DailyMetricsRead[]>('GET', `/metrics/daily_metrics/aggregate?${params}`),
        compare: (params: URLSearchParams) => this.request('GET', `/metrics/daily_metrics/compare?${params}`)
        // etc
    };

    time_entries = {
        ...this.resource<TimeEntryRead, TimeEntryCreate>('/time_tracking/time_entries'),
        summary: (params: URLSearchParams) => this.request<TimeEntryRead[]>('GET', `/time_tracking/time_entries/summary?${params}`),
        aggregate: (params: URLSearchParams) => this.request<TimeEntryRead>('GET', `/time_tracking/time_entries/aggregate?${params}`),
    }

    shopping_list = {
        addItem: (productId: string, quantity: number = 1) => this.request<ShoppingListItemRead>('POST', '/groceries/shopping_list_items', {
            product_id: productId, quantity_wanted: quantity
        }),
        addShortfalls: (recipeId: string) => this.request<ShoppingListItemRead[]>('POST', `/groceries/recipes/${recipeId}/shortfalls_to_list`),
        patchItem: (id: string, data) => this.request<ShoppingListItemRead>('PATCH', `/groceries/shopping_list_items/${id}`, data),
        deleteItem: (id: string) => this.request<ShoppingListItemRead>('DELETE', `/groceries/shopping_list_items/${id}`),
        get: (id: string) => this.request<ShoppingListItemRead[]>('GET', `/groceries/shopping_list`),
    }

    products = this.resource<ProductRead, ProductCreate>('/groceries/products');
    transactions = this.resource<TransactionRead, TransactionCreate, TransactionPatch>('/groceries/transactions');
    recipes = {
        ...this.resource<RecipeRead, RecipeCreate>('/groceries/recipes'),
        cook: (recipeId: string, meal: MealEnum, entryDatetime: string) => this.request('POST', `/groceries/recipes/${recipeId}/cook`, {
            meal: meal,
            entry_datetime: entryDatetime,
        }),
        slots: () => this.request<RecipeSlot[]>('GET', '/groceries/recipe_slots')
    }

    profile = {
        patch: (data: Record<string, string>) => this.request('PATCH', '/profile/me', data)
    }
    user = { patch: (data: Record<string, string>) => this.request('PATCH', '/users/me', data) };
    me = { get: () => this.request<UserMeRead>('GET', '/profile/me') };
    goals = { patch: (data: Record<string, string>) => this.request('PATCH', '/goals/me', data) };
    pillars = { // TODO(api): fixup
        getAll: () => this.request<PillarRead[]>('GET', '/pillars')
    }

    nutrition_log = {
        summary: (params: URLSearchParams) => this.request('GET', `/groceries/nutrition_logs/daily_totals?${params}`),
        logProduct: (data: { product_id: number; grams: number; meal: MealEnum; entry_datetime: string }) =>
            this.request('POST', '/groceries/nutrition_logs', data),
    }

    groceries_dashboard = {
        get: (params: URLSearchParams) => this.request('GET', `/groceries/dashboard?${params}`),
    };

    macros = {
        summary: (params: URLSearchParams) => this.request<MacrosSummaryRead>('GET', `/groceries/macros_summary?${params}`),
    };
}

export const api = new ApiClient();
