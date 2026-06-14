// For commonly-reused API-related functions, fetch for now
import { getJSInstant } from "../datetime";
import { userStore } from "./userStore";
import { Task, Habit, HabitCompletion, DailyMetrics, TimeEntry, Transaction, Product, ShoppingListItem, Recipe, LCRecord } from '../../types';
import { makeToast } from "../ui/toast";


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
    msg: string;
    data: T;
    // errors?: Record<string, string[]>;
};

type ApiErrorResponse = {
    success: false;
    code: string;
    msg: string;
    errors: Record<string, string[]> | null;
}

type ApiResponse<T> = ApiSuccessResponse<T> | ApiErrorResponse;

class ApiError extends Error {
    code: string;
    status: number;
    errors: Record<string, string[]> | null;

    constructor(response: ApiErrorResponse, status: number) {
        super(response.msg);
        this.code = response.code;
        this.status = status;
        this.errors = response.errors;
    }
}

export function handleApiError(err: unknown) {
    if (err instanceof ApiError) {
        if (err.errors) {
            for (const [field, messages] of Object.entries(err.errors)) {
                messages.forEach(msg => makeToast(`${field}: ${msg}`, 'error'));
            }
            // Object.values(err.errors).flat().forEach(msg => makeToast(msg, 'error'));
        } else {
            makeToast(err.message, 'error');
        }
        // makeToast(err.msg, 'error');
    } else {
        makeToast("Unexpected error", 'error');
    }
}

class ApiClient {
    private async request<T = unknown>(
        method: HTTPMethod,
        path: string,
        data?: RequestData
    ): Promise<ApiResponse<T>> {
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
        const responseData: ApiResponse<T> = await response.json();

        if (!responseData.success) {
            // // If .errors -> validation error from Pydantic?
            // if (responseData.errors) {
            //     responseData.errors.forEach(e => makeToast(`${e.loc}: ${e.msg}`, 'error'));
            // // Otherwise -> it's a service/app error more generally
            // } else {
            //     makeToast(responseData.message || 'Something went wrong', 'error');
            // }
            // throw new Error(responseData.message);
            const apiErr = new ApiError(responseData as ApiErrorResponse, response.status);
            handleApiError(apiErr);
            throw apiErr;
        }
        return responseData as ApiSuccessResponse<T>;
    }

    private resource<T>(path: string) {
        return {
            getAll: (params?: URLSearchParams) => this.request<T[]>('GET', `${path}${params ? '?' + params : ''}`),
            getById: (id: string) => this.request<T>('GET', `${path}/${id}`),
            post: (data: any) => this.request<T>('POST', path, data),
            // put: (id: string, data: any) => this.request('PUT', `${path}/${id}`, data),
            patch: (id: string, data: any) => this.request<T>('PATCH', `${path}/${id}`, data),
            delete: (id: string) => this.request<T>('DELETE', `${path}/${id}`),
        };
    }

    tasks = {
        ...this.resource<Task>('/tasks/tasks'),
        toggleComplete: (id: string, isDone: boolean) =>
            this.request<Task>('PATCH', `/tasks/tasks/${id}`, {
                completed_at: isDone ? getJSInstant() : null
            }),
    };

    taskLinks = {
        // TODO: Dbl check this one
        post: (data) => this.request<Task>('POST', '/tasks/task_links', data) 
    }

    habits = {
        ...this.resource<Habit>('/habits/habits')
    }

    habitCompletions = {
        post: (habitId: number) => this.request<HabitCompletion>('POST', `/habits/${habitId}/completions`, {
            completed_at: getJSInstant()
        }),
        deleteToday: (habitId: string) => {
            const today = new Intl.DateTimeFormat('en-CA', {
                timeZone: userStore.data.timezone
            }).format(new Date());
            return this.request('DELETE', `/habits/${habitId}/completions?date=${today}`);
        },
        summary: (params: URLSearchParams) => this.request('GET', `/habits/habit_completions/summary?${params}`),
        heatmap: () => this.request('GET', '/habits/habit_completions/heatmap')
    }

    daily_metrics = {
        ...this.resource<DailyMetrics>('/metrics/daily_metrics'),
        aggregate: (params: URLSearchParams) => this.request<DailyMetrics[]>('GET', `/metrics/daily_metrics/aggregate?${params}`)
        // etc
    };

    time_entries = {
        ...this.resource<TimeEntry>('/time_tracking/time_entries'),
        summary: (params: URLSearchParams) => this.request<TimeEntry>('GET', `/time_tracking/time_entries/summary?${params}`),
        aggregate: (params: URLSearchParams) => this.request<TimeEntry>('GET', `/time_tracking/time_entries/aggregate?${params}`),
    }

    preferences = {
        patch: (data: Record<string, string>) => this.request('PATCH', '/user_preferences/user_preference', data)
    }

    shopping_list = {
        addItem: (productId: string, quantity: number = 1) => this.request<ShoppingListItem>('POST', '/groceries/shopping_list_items', {
            product_id: productId, quantity_wanted: quantity
        }),
        patchItem: (id: string, data) => this.request<ShoppingListItem>('PATCH', `/groceries/shopping_list_items/${id}`, data),
        deleteItem: (id: string) => this.request<ShoppingListItem>('DELETE', `/groceries/shopping_list_items/${id}`),
    }

    products = this.resource<Product>('/groceries/products');
    transactions = this.resource<Transaction>('/groceries/transactions');
    recipes = this.resource<Recipe>('/groceries/recipes');

    profile = {
        patch: (data) => this.request('PATCH', '/profile/me', data)
    }

    nutrition_log = {
        summary: (params: URLSearchParams) => this.request('GET', `/groceries/nutrition_logs/daily_totals?${params}`)
    }

    leetcode_records = {
        ...this.resource<LCRecord>('/habits/leetcode_records')
    }
}

export const api = new ApiClient();
