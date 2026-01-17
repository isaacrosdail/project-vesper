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
