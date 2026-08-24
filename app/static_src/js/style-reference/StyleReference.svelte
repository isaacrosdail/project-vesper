<script lang="ts">
    import { askConfirm } from '../shared/components/ConfirmDialog.svelte';
    import Dropdown from '../shared/components/Dropdown.svelte';
    import { addToast } from '../shared/components/Toaster.svelte';
    import { dragReorder } from './dragReorder';

    const WEATHER = [
        'thunder',
        'sunny-cloud',
        'drizzle',
        'rain',
        'fog',
        'clear',
        'clouds',
        'snow',
        'tornado',
    ];
</script>

<div class="component-catalog" use:dragReorder>

<section draggable="true" class="card-dashboard token-container">
    <h2>Design Tokens</h2>

    <h3>Type</h3>
    <div class="eyebrow">Surfaces — depth comes from value steps</div>
    <p>
        Body copy stays in Manrope; data rides the mono: due
        <time datetime="2026-08-22">Aug 22, 2026</time>, logged at
        <time datetime="2026-08-16T07:30">07:30</time>.
    </p>

    <h3>Surfaces</h3>
    <div class="swatch-strip">
        <div class="swatch" style="background: var(--bg)"><span>bg</span></div>
        <div class="swatch" style="background: var(--surface-1)"><span>bg-light · surface-1</span></div>
        <div class="swatch" style="background: var(--surface-2)"><span>surface-2</span></div>
        <div class="swatch" style="background: var(--surface-3)"><span>bg-hover · surface-3</span></div>
        <div class="swatch" style="background: var(--border-color)"><span>border-color · line</span></div>
        <div class="swatch" style="background: var(--line-strong)"><span>line-strong</span></div>
    </div>
    <h3>Accents</h3>
    <div class="swatch-strip">
        <div class="swatch" style="background: var(--accent-strong); color: var(--text-inverse)">
            <span>accent-strong</span>
        </div>
        <div class="swatch" style="background: var(--accent-hover); color: var(--text-inverse)">
            <span>accent-hover</span>
        </div>
        <div class="swatch" style="background: var(--accent-subtle)">
            <span>accent-subtle</span>
        </div>
        <div class="swatch" style="background: var(--bg-selected)">
            <span>bg-selected</span>
        </div>
    </div>
    <!-- {# Status + text — compact grid of small tiles #} -->
    <div class="swatch-grid">
        <div class="swatch-sm" style="color: var(--text)">text</div>
        <div class="swatch-sm" style="color: var(--text-muted)">text-muted</div>
        <div class="swatch-sm" style="color: var(--text-faint)">text-faint</div>
        <div class="swatch-sm" style="color: var(--text-disabled)">text-disabled</div>
        <div class="swatch-sm" style="background: var(--clr-success); color: var(--text-inverse)">
            success
        </div>
        <div class="swatch-sm" style="background: var(--clr-error); color: var(--text-inverse)">
            error
        </div>
        <div class="swatch-sm" style="background: var(--clr-warning); color: var(--text-inverse)">
            warning
        </div>
        <div class="swatch-sm" style="background: var(--text-muted); color: var(--text-inverse)">neutral</div>
        <div class="swatch-sm" style="background: var(--progress-bar-fill)">progbar</div>
    </div>

    <h3>Badges:</h3>
    <div class="swatch-grid">
        {#each ['low', 'medium', 'high', 'frog'] as p}
            <div class="swatch-sm">
                <svg class="icon" data-priority={p}><use href={`#badge-priority-${p}`}></use></svg>
            </div>
        {/each}
    </div>

    <h3>Weather Icons</h3>
    <div class="swatch-grid">
        {#each WEATHER as w (w)}
            <div class="swatch-sm">
                <svg class="icon"><use href="#icon-weather-{w}"></use></svg>{w}
            </div>
        {/each}
    </div>
</section>

<section draggable="true" class="card-dashboard token-container">
    <h2>Controls</h2>

    <!-- {# Buttons #} -->
    <h3>Buttons</h3>
    <div class="control-row">
        <button class="btn">Base</button>
        <button class="btn btn-primary">Primary</button>
        <button class="btn btn-secondary">Secondary</button>
        <button class="btn btn-destructive">Destructive</button>
        <button class="btn btn-ghost">Ghost</button>
        <button class="btn btn-primary" aria-disabled="true" disabled>Disabled</button>
        <button class="btn btn-primary--gradient">
            <svg class="icon"><use href="#icon-plus"></use></svg>
            <span class="label">Primary--Gradient</span>
        </button>
    </div>
</section>

<section draggable="true" class="card-dashboard token-container">
    <!-- {# Custom controls — get their own visual space #} -->
    <h3>Custom Controls</h3>
    <div class="control-row control-row--spaced">
        <div>
            <label class="control-label">Toggle</label>
            <input type="checkbox" class="toggle-input" id="demo-toggle" />
            <label for="demo-toggle" class="toggle"></label>
        </div>
        <!-- {#{ ui.timeframe_pills("style-ref") }#} -->
    </div>

    <h3>Pill Group (multi-select checkboxes)</h3>
    <fieldset class="pill-group">
        {#each ['Health', 'Career', 'Purpose', 'Rest', 'Relationships'] as p, idx}
            <label class="pill">
                <input
                    type="checkbox"
                    name="demo-pills"
                    value={p.toLowerCase()}
                    checked={idx % 2 === 0} />
                <span>{p}</span>
            </label>
        {/each}
    </fieldset>

    <div class="tertiary another-pill">On track today</div>

    <div>
        <label class="control-label">Segmented</label>
        <!-- {{ ui.segmented(
            'test',
            [('one', 'One'), ('two', 'Two'), ('three', 'Three')],
            'Test segmented'
        ) }} -->
    </div>

    <div class="tab-group segmented" role="tablist">
        <!-- <button type="button" role="tab" data-tab="steps" class="tab">{{ ui.steps_svg() }} Steps</button>
        <button type="button" role="tab" data-tab="weight" class="tab">{{ ui.scale_svg() }} Weight</button>
        <button type="button" role="tab" data-tab="sleep" class="tab">{{ ui.sleep_svg() }} Sleep</button>
        <button type="button" role="tab" data-tab="calories" class="tab">{{ ui.calories_svg() }} Calories</button> -->
    </div>
</section>

<section draggable="true" class="card-dashboard token-container">
    <!-- {# Specialized inputs — only the ones that look different #} -->
    <h3>Input Types</h3>
    <div class="control-grid">
        <div>
            <label class="control-label">Date</label>
            <input type="date" />
        </div>
        <div>
            <label class="control-label">Time</label>
            <input type="time" />
        </div>
        <div>
            <label class="control-label">Number</label>
            <input type="number" placeholder="72.4" step="0.1" />
        </div>
        <div>
            <label class="control-label">Select</label>
            <select>
                <option>Option 1</option>
                <option>Option 2</option>
            </select>
        </div>
        <div>
            <label class="control-label">Textarea</label>
            <textarea placeholder="Textarea" rows="2"></textarea>
        </div>
        <div>
            <label class="control-label">Password</label>
            <div class="password-input-group">
                <input type="password" id="demo-password" placeholder="Password" />
                <button type="button" class="btn-icon" data-password-toggle="demo-password">
                    <!-- {{ ui.eye_slash_svg() }} -->
                </button>
            </div>
        </div>
    </div>

    <!-- {# Input states - one input type, multiple states #} -->
    <h3>Input States</h3>
    <form class="control-grid" novalidate>
        <div>
            <label class="control-label">Default</label>
            <input type="text" placeholder="Default" />
        </div>
        <div>
            <label class="control-label">Invalid</label>
            <input type="text" class="invalid" value="Bad value" />
        </div>
        <div>
            <label class="control-label">Disabled</label>
            <input type="text" disabled value="Disabled" />
        </div>
    </form>
</section>

<section draggable="true" class="card-dashboard surface">
    <h2>Feedback</h2>

    <!-- {# Dialogs — modal + confirmation on one row #} -->
    <h3>Dialogs</h3>
    <div class="control-row">
        <button class="btn btn-primary" onclick={async () => await askConfirm('Yah?')}
            >Confirmation</button>
    </div>

    <!-- {# Toasts — single row #} -->
    <h3>Toasts</h3>
    <div class="control-row">
        <button class="btn btn-primary" onclick={() => addToast('INFO', 'This is a test', 'info')}
            >Info</button>
        <button
            id="toast-success"
            class="btn btn-secondary"
            onclick={() => addToast('ERR', 'This is a test', 'error')}>Error</button>
        <button
            id="toast-error"
            class="btn btn-secondary"
            onclick={() => addToast('SUCCESS', 'This is a test', 'success')}>Success</button>
    </div>

    <!-- {# Tooltip #} -->
    <h3>Tooltip</h3>
    <div class="control-row control-row--spaced">
        <div class="tooltip" id="no-after">Tooltip styling</div>
        <button
            class="btn btn-secondary"
            data-tip="Hover to see positioning">Hover me</button>
    </div>

    <!-- {# Dropdown #} -->
    <h3>Dropdown</h3>
    <div class="control-row">
        <Dropdown
            label="Test Dropdown"
            opts={[
                ['Yah', 'yah'],
                ['Nah', 'nah'],
            ]}
            onSelect={(v) => addToast('Picked', v, 'info')} />
    </div>
</section>

</div>


<style>
    .component-catalog {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
    gap: 1.5rem;
    }
    /* Token swatches */
    .swatch-strip {
        display: flex;
        border-radius: var(--border-radius);
        overflow: hidden;
        border: var(--border-default);
    }
    .swatch-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
        gap: var(--space-sm);
    }
    .swatch {
        flex: 1;
        padding: var(--space-sm) var(--space-md);
        font-size: var(--font-size-sm);
    }

    .swatch-sm {
        padding: var(--space-sm);
        border-radius: var(--border-radius-mild);
        font-size: var(--font-size-sm);
        text-align: center;
        border: var(--border-default);
    }

    /* To make border-color clearly visible for tuning */
    .token-container {
        border: 4px solid var(--border-color);
    }
    .control-row {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: var(--space-sm);
    }

    .control-row--spaced {
        gap: var(--space-lg);
    }

    .control-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: var(--space-md);
    }

    .control-label {
        display: block;
        font-size: var(--font-size-sm);
        color: var(--text-muted);
        margin-bottom: var(--space-xs);
    }

</style>
