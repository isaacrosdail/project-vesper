

type ApiResponse = {
    success: boolean;
    message: string;
    data?: any; // Could be list, dict, etc. Consider using generics in future
    errors?: any;
};

declare function apiRequest( // gives us a "callable symbol" - is the function the "symbol"? Tokenizer term or? -> NO. Diff concepts.
    method: string,
    endpoint: string,
    data?: RequestData | null,
    options?: {
        onSuccess?: (response: ApiResponse) => void;
        onFailure?: (response: ApiResponse) => void;
    }
): Promise<ApiResponse>


// in api.ts, we had:
type RequestData = 
    | { [key: string]: string | number | boolean | null | undefined }
    | FormData;


/*There are some issues here. So [key: string] is the index signature. It says:
    "This object can have any property name (any string), and the val will be of type X."
*/

const url = 'myurl';

// Why this is too restrictive for JSON:
// This type DOESN'T allow:
apiRequest('POST', url, { items: [1, 2, 3] });      // Arrays - not allowed!
// Nested objects - not allowed!
apiRequest('POST', url, { user: { name: "Bob" } })  // Nested objects - not allowed!


// To fix this, we can just add typings for: 1) nested objects and 2) arrays

type JsonValue = 
    | string | number | boolean | null  // primitives
    | { [key: string]: JsonValue }      // objects (can nest because JsonValue is recursive here)
    | JsonValue[];                      // arrays (can also contain JsonValue)

// Allows for the following as well:
const payload1 = [1, 2, 3];
const payload2 = { user: { name: "Bob" } }