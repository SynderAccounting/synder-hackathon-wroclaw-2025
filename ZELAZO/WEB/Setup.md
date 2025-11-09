# 1. Install deps
cd /WEB
npm i

# 2. Start web
npm run dev

# 3. Close connection 
terminal: control + C

# 4. Kill zombies localhosts
lsof -tiTCP:5173-5180 -sTCP:LISTEN | xargs kill -9

# 5. Set new endpoint
cd /WEB/vite.config.js and change target: 'https://susceptible-liv-issuably.ngrok-free.dev',
