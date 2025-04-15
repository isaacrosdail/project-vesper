/**
 * @jest-environment jsdom
 */

const { updateFieldDisplay } = require('../tasks/dashboard');

test('updates td with new span element containing new value', () => {
    const td = document.createElement('td');
    td.innerHTML = '<input value="Old Title">';

    updateFieldDisplay(td, 'New Title');

    expect(td.children.length).toBe(1);
    expect(td.firstChild.tagName).toBe('SPAN');
    expect(td.textContent).toBe('New Title');
});