# Development Setup

## Docker Configs
- `docker-compose.yml` - Local development (database only)
- `docker-compose.prod.yml` - Full production stack with Nginx
- `docker-compose.pi.yml` - My Raspberry Pi deployment

## Development Tools

### TypeScript & Linting

**Commands:**
- `npm run lint` - Check for issues

### Pre-Commit Hooks
Husky runs automatic checks before each commit:
- Linting
- Type checking
- Security audit

To bypass: `git commit --no-verify` OR (for the session) simply do `export HUSKY=0`

## Setup / General Config Stuff

1. Install Docker (on linux)
```
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt install docker-compose
```

2. Install Node.js (on linux)
```
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs
```

## Package.json Scripts:
```json
"build": "cross-env NODE_ENV=production tailwindcss -i .app/static/css/input.css -o .app/static/css/output.css --minify"
```
```json
"scripts": {
"tailwind": "npx tailwindcss -i ./app/static/css/style.css -o ./app/static/css/output.css --watch",
"flask": "flask run --debug",
"sync": "browser-sync start --proxy localhost:5000 --files 'app/**/templates/**/*.html' 'static/css/*.css'",
"dev": "concurrently \"npm:tailwind\" \"npm:flask\" \"npm:sync\""
}
```

## Dependencies Reasoning
- cross-env ->
- browser-sync -> Live reloads, part of npm run dev script
- concurrently -> ????
- jest-environment-jsdom -> Needed for Jest to mimic DOM?
