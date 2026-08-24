
<script lang="ts">
    import { fetchWeatherData } from '../shared/services/weather-service';
    import { fmtTime } from '../shared/datetime';
    import type { WeatherResult } from '../types';
    import { userState } from '../shared/services/userState.svelte';
    import { nowUser } from '../shared/datetime';

    let { name = null }: { name?: string | null } = $props();

    // let now = $state(new Date());
    let now = $state(nowUser());
    let weather = $state<WeatherResult | null>(null);

    $effect(() => {
        const clock = setInterval(() => now = nowUser(), 30_000);
        return () => clearInterval(clock);
    });

    async function loadWeather() {
        if (!userState.me || !location) return;
        const { unit_system } = userState.me.profile;
        const { city, country } = location;
        weather = await fetchWeatherData(city, country, unit_system);
    }
    $effect(() => {
        loadWeather();
        const hourly = setInterval(loadWeather, 60 * 60 * 1000);
        return () => clearInterval(hourly);
    });

    const NOON = 12, EVENING = 18;
    const greeting = $derived(
        now.hour < NOON ? 'Good morning'
        : now.hour < EVENING ? 'Good afternoon'
        : 'Good evening'
    );

    const tempUnit = $derived(userState.me?.profile.unit_system === 'metric' ? 'C' : 'F');

    // pure port of updateSky — same math, returns values instead of patching style
    function calcCelestialBodyPos(startTime: number, endTime: number, nowSec: number) {
        const progress = (nowSec - startTime) / (endTime - startTime);
        const clamped = Math.max(0, Math.min(1, progress));
        return { x: clamped, y: Math.sin(clamped * Math.PI) };
    }

    const sky = $derived.by(() => {
        if (!weather) return null;
        const { sunrise, sunset } = weather;
        const nowSec = Math.floor(now.epochMilliseconds / 1000);
        const isDay = nowSec >= sunrise && nowSec <= sunset;
        const startTime = isDay ? sunrise : (nowSec > sunset ? sunset : sunset - 86400);
        const endTime = isDay ? sunset : (nowSec > sunset ? sunrise + 86400 : sunrise);
        const pos = calcCelestialBodyPos(startTime, endTime, nowSec);
        return {
            top:    isDay ? '#4a90d9' : '#0a1628',
            bottom: isDay ? '#87ceeb' : '#1a2a4a',
            x: `${pos.x * 100}%`,
            y: `${pos.y * 100}%`,
        };
    });

    const location = $derived.by(() => {
        const p = userState.me?.profile;
        return p?.city && p?.country ? { city: p.city, country: p.country } : null;
    })
</script>

<section id="greeting-card" class="card-dashboard surface"
    class:has-sky={sky}
    style:--sky-top={sky?.top} style:--sky-bottom={sky?.bottom}
    style:--celestial-x={sky?.x} style:--celestial-y={sky?.y}>
    <div class="card-title">
        <h2>{greeting}{name ? `, ${name}` : ''}!</h2>
    </div>

    <div class="greeting-content">
        <p><span id="time-display">{fmtTime(now.toString())}</span> |
            <!-- {formatToUserTimeString(now, { weekday: 'short', month: 'short', day: 'numeric' })}--></p>
        <div class="weather-info">
            {#if location}
                {#if weather}
                    <div id="weather-temp">
                        {weather.temp}°{tempUnit}
                        <svg class="icon"><use href="#{weather.emoji}"></use></svg>
                        - {userState.me?.profile.city ?? ''}
                    </div>
                    <div id="weather-sunset">Sunset {weather.sunsetFormatted}</div>
                {:else}
                    <div id="weather-temp">Loading weather info...</div>
                {/if}
            {/if}
        </div>
    </div>
</section>

<style>
    #greeting-card {
        position: relative;
        height: clamp(150px, 15vh, 300px);

        & canvas {
            position: absolute;
            inset: 0;
            z-index: 0;
            width: 100%;
        }
        & .greeting-content {
            position: relative;
            z-index: 1;
            display: flex;
            justify-content: space-between;
            /* width: 100%; */
        }
        & .weather-info {
            display: flex;
            align-items: center;
            gap: var(--space-sm);
        }
        & .weather-temp {
            display: flex;
            align-items: center;
        }
    }

    #greeting-card::before {
        display: none;
        content: '';
        position: absolute;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: var(--celestial-color, gold);
        left: var(--celestial-x, 50%);
        bottom: var(--celestial-y, 50%);
        box-shadow: 0 0 20px var(--celestial-color, gold);
        transition: left 1s ease, bottom 1s ease;
    }
    #greeting-card.has-sky::before { display: block; }
</style>