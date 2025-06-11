
const { calcSunPosition } = require('@/index.js');


test('basic math works', () => {
    expect(2 + 2).toBe(4);
})


// Testing our calcSunPosition function
test('calculates sun position at noon (midday)', () => {
    // Arrange: 
    const sunrise = 1749613415; // Unix timestamp
    const sunset = 1749673017;
    const midday = sunrise + ((sunset - sunrise) / 2); // 1749643216

    // Act
    const result = calcSunPosition(sunrise, sunset, midday);

    // Assert
    expect(result.x).toBe(0.5);
    expect(result.y).toBeCloseTo(1, 5); // "Should be approx 1, accurate to 5 decimal places" (so 0.99999 would pass, but 0.9999 wouldn't)
})