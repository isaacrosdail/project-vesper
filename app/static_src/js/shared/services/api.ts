// For commonly-reused API-related functions, fetch for now

type ApiResponse = {
    success: boolean;
    message: string;
    data?: unknown;
    errors?: unknown;
};

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

export const routes = {
  groceries: {
    products: {
      collection: '/groceries/products',
      item: (id: string) => `/groceries/products/${id}`,
    },
    transactions: {
      collection: '/groceries/transactions',
      item: (id: string) => `/groceries/transactions/${id}`,
    },
    shopping_lists: {
      collection: '/groceries/shopping_lists',
      item: (id: string) => `/groceries/shopping_lists/${id}`,
    },
    shopping_list_items: {
      collection: '/groceries/shopping_list_items',
      item: (id: string) => `/groceries/shopping_list_items/${id}`,
    },
    recipes: {
      collection: '/groceries/recipes',
      item: (id: string) => `/groceries/recipes/${id}`,
    },
    recipe_ingredients: {
      collection: '/groceries/recipe_ingredients',
      item: (id: string) => `/groceries/recipe_ingredients/${id}`,
    },
  },
  tasks: {
    tasks: {
      collection: '/tasks/tasks',
      item: (id: string) => `/tasks/tasks/${id}`,
    },
  },
  habits: {
    habits: {
      collection: '/habits/habits',
      item: (id: string) => `/habits/habits/${id}`,
    },
    habit_completions: {
      collection: '/habits/habit_completions',
      item: (id: string) => `/habits/habit_completions/${id}`,
      summary: (params: URLSearchParams) => `/habits/habit_completions/summary?${params}`
    },
    leet_code_records: {
      collection: '/habits/leet_code_records',
      item: (id: string) => `/habits/leet_code_records/${id}`,
    },
  },
  metrics: {
    daily_metrics: {
      collection: '/metrics/daily_metrics',
      item: (id: string) => `/metrics/daily_metrics/${id}`,
      timeseries: (params: URLSearchParams) => `/metrics/daily_metrics/timeseries?${params}`
    },
  },
  time_tracking: {
    time_entries: {
      collection: '/time_tracking/time_entries',
      item: (id: string) => `/time_tracking/time_entries/${id}`,
      summary: (params: URLSearchParams) => `/time_tracking/time_entries/summary?${params}`
    },
  },
};

/**
 * Makes an API request & handles the response.
 * Automatically prepends '/api' to endpoints.
 * @param method HTTP method
 * @param endpoint API endpoint path (ex: '/groceries/products/123')
 * @param data Optional request body (plain obj for JSON or FormData)
 * @param onSuccess - Optional callback when request succeeds
 * @param onFailure - Optional callback when request fails
 */
export async function apiRequest(
    method: string,
    endpoint: string,
    data: RequestData = null,
    { onSuccess, onFailure }: {
        onSuccess?: (responseData: ApiResponse) => void,
        onFailure?: (responseData: ApiResponse) => void
    } = {}
): Promise<ApiResponse> {
    try {
        const isFormData = data instanceof FormData; // formData objs: must lack a Content-Type header AND not be stringified
        const url = `/api${endpoint}`;

        if (!window.csrfToken) {
            console.error('CSRF token missing');
            throw new Error('CSRF token not found');
        }

        const headers = new Headers({ 'X-CSRFToken': window.csrfToken });
        if (!isFormData) {
            headers.set('Content-Type', 'application/json');
        }

        const response = await fetch(url, {
            method,
            headers,
            body: isFormData ? data : (data ? JSON.stringify(data) : null)
        });
        const responseData: ApiResponse = await response.json();

        if (responseData.success) {
            onSuccess?.(responseData);
            return responseData;
        } else {
            onFailure?.(responseData);

            if (!onFailure) {
                console.error('Server error: ', responseData.message);
            }
            throw new Error(responseData.message);
        }
    } catch (error: unknown) {
        console.error(`Error with ${method} request:`, error);
        throw error; // re-throw so await can catch it?
    }
}
