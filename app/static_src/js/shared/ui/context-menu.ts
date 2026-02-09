
/*
 * Lightweight context menu utility.
 * 
 * Usage:
 *   contextMenu.create({
 *     position: { x: rect.left, y: rect.bottom },
 *     items: [
 *       { label: 'Edit', action: () => handleEdit() },
 *       { label: 'Delete', action: () => handleDelete() }
 *     ]
 *   });
 */

type ContextMenuItem = {
    label: string;
    action: () => void | Promise<void>;
}

type ContextMenuConfig = {
    position: {x: number, y: number};
    items: ContextMenuItem[];
}

class ContextMenu {
    private isCreating = false;

    constructor() {
        this.setupGlobalListeners();
    }

    private setupGlobalListeners(): void {
        // Close when clcking outside of menu
        document.addEventListener('click', (e) => {
            if (this.isCreating) {
                return;
            }
            const menu = document.querySelector('.context-menu');
            const target = e.target as Node;

            if (menu && !menu.contains(target)) {
                this.close();
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.close();
            }
        });
    }

    create(config: ContextMenuConfig): void {
        this.close();
        this.isCreating = true; // prevent global click listener from auto-closing

        if (config.items.length === 0) {
            console.warn('ContextMenu: No items provided');
            this.isCreating = false;
            return;
        }

        const menu = document.createElement('ul');
        menu.classList.add('context-menu');

        // Build menu items & append to DOM
        config.items.map(item => {
            const li = document.createElement('li');
            li.textContent = item.label;

            li.addEventListener('click', async() => {
                // Note: await is only needed since some actions might be async
                try {
                    await item.action(); // execute stored function
                    this.close();
                } catch (error) {
                    console.error('ContextMenu action failed: ', error);
                    this.close();
                }
            });

            menu.appendChild(li);
        });

        menu.style.left = config.position.x + 'px';
        menu.style.top = config.position.y + 'px';
        menu.style.display = 'block';

        document.body.appendChild(menu);

        // Defer reset to prevent immediate close
        setTimeout(() => {
            this.isCreating = false;
        }, 0); // next tick
    }

    close(): void {
        document.querySelector('.context-menu')?.remove();
    }
}

// Export singleton instance
export const contextMenu = new ContextMenu();