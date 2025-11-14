// For commonly-reused API-related functions, fetch for now

type ApiResponse = {
    success: boolean;
    message: string;
    data?: any; // Could be list, dict, etc. Consider using generics in future
    errors?: any;
};

/**
 * Makes an API request & handles the response.
 * Automatically prepends '/api' to endpoints.
 * @param method HTTP method
 * @param endpoint API endpoint path (ex: '/groceries/products/123')
 * @param onSuccess Callback invoked when response.success
 * @param data Optional request body (plain obj for JSON or FormData)
 */
export async function apiRequest(
    method: string,
    endpoint: string,
    onSuccess: (responseData: ApiResponse) => void,
    data: Record<string, any> | FormData | null = null
) {
    try {
        const isFormData = data instanceof FormData; // formData objs need to not have a Content-Type header AND not be stringified
        const url = `/api${endpoint}`;

        const response = await fetch(url, {
            method,
            headers: isFormData ? {} : { 'Content-Type': 'application/json' },
            body: isFormData ? data : (data ? JSON.stringify(data) : null)
        });
        const responseData: ApiResponse = await response.json();

        if (responseData.success) {
            onSuccess(responseData);
        } else {
            console.error('Server error: ', responseData.message);
        }
    } catch (error: unknown) {
        console.error(`Error with ${method}:`, error);
    }
}