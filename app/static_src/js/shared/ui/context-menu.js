

// TODO: Properly implement & wire into tables.js functionalities
function createContextMenu(e) {
    if (e.target.closest('.table-row')) {
        // Accessing OR making our custom context menu
        let menu = document.querySelector('.context-menu');
        if (!menu) {
            menu = document.createElement('ul');
            const menuItems = ['Edit', 'Delete', 'Close'];
        
            const menuElements = menuItems.map(item => {
                const menuItem = document.createElement('li');
                menuItem.textContent = item;
                return menuItem;
            });
            menuElements.forEach(element => menu.appendChild(element));
            menu.classList.add('context-menu');
        }

        // Position menu at cursor
        menu.style.left = e.clientX + 'px';
        menu.style.top = e.clientY + 'px';
        menu.style.display = 'block';
        document.body.appendChild(menu); // createElement adds to JS mem, appendChild to add to DOM
    }
}

document.addEventListener('contextmenu', (e) => {
    if (e.ctrlKey) {
        console.log('shift pressed!');
        e.preventDefault();
        createContextMenu(e); // TODO?: Pull our context menu handling into some kind of global.js
    }
});

// Click away for context menu close
document.addEventListener('click', (e) => {
    if (!e.target.matches('.context-menu')) {
        const menu = document.querySelector('.context-menu');
        menu?.remove();
    }
});