
export function setupCanvas() {
    const canvas = document.querySelector('#sky-canvas');
    const rect = canvas.getBoundingClientRect();

    // Set internal resolution to display size
    canvas.width = rect.width;
    canvas.height = rect.height;
}

const MARGIN_X = 0.1; // 10% margin left/right
const MARGIN_Y = 0.15; // 15% margin top/bottom

class CelestialRenderer {
    constructor(canvasId) {
        this.canvas = document.querySelector(canvasId);
        this.ctx = this.canvas.getContext('2d');
    }
    draw(x, y, type) {
        const config = CELESTIAL_CONFIGS[type];

        // Convert normalized coordinates to canvas pixels
        const canvasX = (MARGIN_X + x * (1 - 2 * MARGIN_X)) * this.canvas.width;
        const canvasY = (MARGIN_Y + y * (1 - 2 * MARGIN_Y)) * this.canvas.height;
        
        // Set up coordinate system with bottom-left origin
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.ctx.save();
        this.ctx.scale(1, -1);
        this.ctx.translate(0, -this.canvas.height);

        // Draw main body (sun or moon)
        this.ctx.fillStyle = config.COLOR;
        this.ctx.beginPath();
        this.ctx.arc(canvasX, canvasY, config.RADIUS, 0, 2 * Math.PI);
        this.ctx.fill();

        // Draw rays (only for sun)
        if (type === 'sun'){
            this.ctx.strokeStyle = config.COLOR;
            for (let i = 0; i < config.RAY_COUNT; i++) {
                const angle = (i * 2 * Math.PI) / config.RAY_COUNT;
                const startX = canvasX + (config.RADIUS + 5) * Math.cos(angle);
                const startY = canvasY + (config.RADIUS + 5) * Math.sin(angle);
                const endX = canvasX + (config.RADIUS + config.RAY_LENGTH) * Math.cos(angle);
                const endY = canvasY + (config.RADIUS + config.RAY_LENGTH) * Math.sin(angle);
            
                this.ctx.beginPath();
                this.ctx.moveTo(startX, startY);
                this.ctx.lineTo(endX, endY);
                this.ctx.stroke();
            }
        // Draw some craters in the moon
        } else {
            // this.ctx.fillStyle = 'rgba(80, 80, 80, 0.4)';
            const craterCount = 3;
            for (let i = 0; i < craterCount; i++) {
                // Vary crater shade
                const shade = 100 + Math.floor(Math.random() * 50); // 100-150 grey
                this.ctx.fillStyle = `rgb(${shade}, ${shade}, ${shade})`;
                // Random polar coords
                const angle = Math.random() * 2 * Math.PI; // rand direction, 0-360 deg (JS angles are in radians -> 2pi radians = 360 deg)
                const radius = Math.sqrt(Math.random()) * config.RADIUS; // random dist from center
                // Convert to Cartesian
                const x = canvasX + radius * Math.cos(angle);
                const y = canvasY + radius * Math.sin(angle);

                this.ctx.beginPath();
                this.ctx.arc(x, y, radius, 0, 2 * Math.PI);
                this.ctx.fill();
            }

            // Last pass: mask everything outside the moon to 'shave off' craters that spill over
            this.ctx.save(); // apparently save pushes to a stack and restore pops => therefore, we can nest these
            this.ctx.globalCompositeOperation = "destination-in";
            this.ctx.beginPath();
            this.ctx.arc(canvasX, canvasY, config.RADIUS, 0, 2 * Math.PI);
            this.ctx.fill();
            this.ctx.restore();
        }
        this.ctx.restore(); // reset canvas to point of .save()
    }
}


/**
 * Calculates normalized sun position along arc for the current time
 * @param {number} start - Sunrise time in ms (Unix)
 * @param {number} end - Sunset time in ms (Unix)
 * @param {number} now - Current time in ms (Unix)
 * @returns {{x: number, y: number}} Normalized coordinates (0-1) for sun position
 * @description
 * - X represents progress through the day (0 = sunrise, 1 = sunset)
 * - Y uses sine curve to create natural arc (0 at horizon, peak at noon)
 * - Want to extend for moon calculation using night hours later
 */
export function calcCelestialBodyPos(start, end, now) {
    const xVal = (now - start) / (end - start);
    const yVal = (Math.sin(xVal * Math.PI));

    return { x: xVal, y: yVal };
}

// Sun drawing constants
const CELESTIAL_CONFIGS = {
    sun: {
        RADIUS: 15,
        RAY_COUNT: 8,
        RAY_LENGTH: 10,
        RAY_OFFSET: 5, // gap between sun & its rays
        COLOR: 'orange'
    },
    moon: {
        RADIUS: 15,
        RAY_COUNT: 0,
        RAY_LENGTH: 0,
        RAY_OFFSET: 0,
        COLOR: 'grey'
    }
};

// Setup on load & resize
if (document.querySelector('canvas')) {
    setupCanvas();
}

export { CelestialRenderer };