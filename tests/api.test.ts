
import { beforeEach, describe, expect, mock, test } from 'bun:test';

// Mock fetch()
const toastSpy = mock(() => {});
// Mock factory: replaces the whole toast module, not just makeToast
mock.module('../app/static_src/js/shared/ui/toast', () => ({
    makeToast: toastSpy,
}));

const { api, ApiError } = await import('../app/static_src/js/shared/services/api');

// Replaces global.fetch: ignore the network and returns the response we make ourselves
function mockFetch(body: BodyInit, status = 200) {
    const fetchMock = mock(async () => new Response(body, { status }));
    global.fetch = fetchMock as unknown as typeof fetch;
    return fetchMock;
}

function jsonResponse(e: unknown, status = 200) {
    return mockFetch(JSON.stringify(e), status);
}

beforeEach(() => {
    window.csrfToken = 'test-token';
    toastSpy.mockClear();
});

describe('request', () => {
    test('success envelope resolves with data and message', async () => {
        const fetchMock = jsonResponse({ success: true, message: 'ok', data: [{ id: 1 }] });
        
        const resp = await api.products.getAll();

        expect(resp.data).toEqual([{ id: 1 }]);
        expect(resp.message).toBe('ok');

        // fetchMock.mock records api calls (ie our api.products.getAll() above)
        const [url, init] = fetchMock.mock.calls[0];
        expect(url).toBe('/api/groceries/products');
        expect((init.headers as Headers).get('X-CSRFToken')).toBe('test-token');
    });

    test('error', async () => {
        jsonResponse({ success: false, message: 'failed', code: 'SERVICE_ERROR', errors: null },
            409,
        );

        try {
            await api.products.getById("1");
            expect.unreachable('request should have thrown');
        } catch (err) {
            expect(err).toBeInstanceOf(ApiError);
            expect(err.status).toBe(409);
            expect(err.code).toBe('SERVICE_ERROR');
            expect(err.message).toBe('failed');
        }
        expect(toastSpy).toHaveBeenCalledTimes(1);
        expect(toastSpy).toHaveBeenCalledWith('failed', 'error');
    });

    test('missing csrf-token means fetchMock is never called', async () => {
        const fetchMock = jsonResponse({ success: true, message: 'Never' });
        window.csrfToken = '';

        try {
            await api.products.getAll();
            expect.unreachable('request should have thrown on missing token');
        } catch (err) {
            expect(err).toBeInstanceOf(Error);
            expect((err as Error).message).toBe('CSRF token not found');
            expect(fetchMock).toHaveBeenCalledTimes(0);
        }
    });

    test('non-json response throws with invalid response', async () => {
        const fetchMock = mockFetch('<html>Not found</html>', 404);

        try {
            await api.daily_metrics.getAll();
            expect.unreachable('request should have thrown');
        } catch (err) {
            expect(err).toBeInstanceOf(ApiError);
            expect(err.code).toBe('INVALID_RESPONSE');
            expect(err.message).toBe('Server returned an unexpected response');
        }
        expect(toastSpy).toHaveBeenCalledTimes(1);
    });

});
