// For commonly-reused API-related functions, fetch for now

export async function apiRequest(method, url, onSuccess, data = null) {
    try {
        const isFormData = data instanceof FormData; // formData objs needs to not have a Content-Type header AND not be stringified

        const response = await fetch(url, {
            method,
            headers: isFormData ? {} : { 'Content-Type': 'application/json' },
            body: isFormData ? data : (data ? JSON.stringify(data) : null)
        });
        const responseData = await response.json();

        if (responseData.success) {
            onSuccess(responseData);
        } else {
            console.error('Server error: ', responseData.message);
        }
    } catch (error) {
        console.error(`Error with ${method}:`, error);
    }
}