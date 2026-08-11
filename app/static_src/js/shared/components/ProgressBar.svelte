<script lang="ts">
    import { randFloat, randInt } from '../utils';

    let {
        completed,
        total,
        label,
    }: {
        completed: number;
        total: number;
        label: string;
    } = $props();

    const percent = $derived(total > 0 ? (completed / total) * 100 : 0);
    const surging = $derived(percent >= 90 || total - completed === 1);

    let barEl: HTMLDivElement;
    let prev = -1;
    $effect(() => {
        if (total > 0 && completed === total && prev >= 0 && prev < total) {
            triggerConfetti(barEl);
        }
        prev = completed;
    });

    function triggerConfetti(el: HTMLElement) {
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (prefersReducedMotion) return;

        const progressBarBox = el.getBoundingClientRect();
        const confettiLayer = document.querySelector('#confetti-layer');
        if (!confettiLayer) {
            console.error('Confetti emitter div not found');
            return;
        }

        // SETTINGS
        const shapeClasses = ['star', 'circle', 'diamond', 'parallelogram', 'triangle'];
        const numDots = randInt(15, 40);
        const baseSize = parseFloat(
            getComputedStyle(document.documentElement).getPropertyValue('--confetti-size-base'),
        );

        // Generate each confetti dot
        for (let i = 0; i < numDots; i++) {
            const dot = document.createElement('div');
            dot.classList.add('confetti-dot', shapeClasses[i % shapeClasses.length]!);

            // Position dot at right edge of progress-bar
            dot.style.position = 'absolute';
            dot.style.left = `${progressBarBox.right}px`;
            dot.style.top = `${progressBarBox.top + progressBarBox.height / 2}px`;

            // Generate Bezier path (curved + falling)
            const endX = randInt(-150, 150); // horizontal arc/spread
            const endY = randInt(-120, -250); // apex
            const fallY = randInt(200, 250); // fall distance
            const controlX = randInt(endX * 0.4, endX * 0.6);
            const controlY = randInt(endY - 30, endY + 30);
            const path = `M 0 0 Q ${controlX} ${controlY} ${endX} ${endY} T ${endX} ${fallY}`;

            // Animation Timings
            const animationTime = randFloat(1.5, 3);
            const animationDelay = randFloat(0.9, 1);
            const tumbleSpeed = randFloat(0.6, 1.5);
            const scale = baseSize * randFloat(4, 5); // size scaling (semi-responsive)

            // Assign styles & animations
            dot.style.setProperty('--scale', String(scale));
            dot.style.offsetPath = `path('${path}')`;
            dot.style.animation =
                `follow-path ${animationTime}s cubic-bezier(0.25, 0.7, 0.9, 0.3) ${animationDelay} forwards, ` +
                `tumble ${tumbleSpeed}s linear infinite`;

            // Insert into confetti layer & tidy up when done
            confettiLayer.appendChild(dot);
            dot.addEventListener('animationend', () => dot.remove());
        }
    }
</script>

<div class="progress-bar-container">
    <div class="progress-bar" bind:this={barEl}>
        <div class="progress-bar-fill" class:surging style:transform="scaleX({percent / 100})">
        </div>
    </div>
    <span class="progress-text">{label}: {completed} of {total}</span>
</div>

<style>
    .progress-bar-container {
        display: flex;
        flex-direction: column;
    }

    .progress-bar,
    .progress-bar-fill {
        height: 1.25rem;
    }
    .progress-bar {
        width: 80%;
        max-width: 300px;
        overflow: hidden; /* make rounded edges clean on lower percentages, effectively 'clips' overlap */
        background-color: var(--progress-bar-bg);
        border: var(--border-default);
        border-radius: var(--border-radius);
    }
    .progress-bar-fill {
        position: relative; /* positioning context for progress-bar-fill::after */
        overflow: hidden; /* clips our ::after's pulsing effect cleanly */
        background: var(--progress-bar-fill);
        transform: scaleX(0); /* JS can set scaleX using our percent progress directly this way */
        transform-origin: left; /* fill acts as a mask, 'peels back' to reveal gradient of progress-bar */
        transition: transform 0.2s ease-in-out;

        &::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 50%;
            height: 100%;
        }
        &.surging {
            animation: pulse 1.5s ease-in-out infinite;

            &::after {
                background: linear-gradient(
                    to right,
                    transparent,
                    rgb(255 255 255 / 40%),
                    transparent
                );
                animation: surge 1.5s ease-in-out infinite;
            }
        }
    }
</style>
