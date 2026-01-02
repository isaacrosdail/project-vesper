// For commonly-reused API-related functions, fetch for now

type ApiResponse = {
    success: boolean;
    message: string;
    data?: any; // Could be list, dict, etc. Consider using generics in future
    errors?: any;
};

// Exclude functions/callbacks from data
type RequestData = 
    | { [key: string]: string | number | boolean | null | undefined }
    | FormData;

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
    data: RequestData | null = null,
    { onSuccess, onFailure }: {
        onSuccess?: (responseData: ApiResponse) => void,
        onFailure?: (responseData: ApiResponse) => void
    } = {}
): Promise<ApiResponse> {
    try {
        const isFormData = data instanceof FormData; // formData objs: must lack a Content-Type header AND not be stringified
        const url = `/api${endpoint}`;

        const response = await fetch(url, {
            method,
            headers: isFormData ? {} : { 'Content-Type': 'application/json' },
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