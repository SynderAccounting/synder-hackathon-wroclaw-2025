# ngrok Public URL Setup Guide

This guide explains how to expose your backend API publicly using ngrok.

## Prerequisites

1. **Install ngrok**:
   - **Windows**:
     - Download from https://ngrok.com/download
     - Or use: `choco install ngrok` (Chocolatey)
     - Or use: `scoop install ngrok` (Scoop)
   - **macOS**: `brew install ngrok/ngrok/ngrok`
   - **Linux**: `snap install ngrok`

2. **Get ngrok authtoken**:
   - Sign up at https://ngrok.com
   - Get your token from: https://dashboard.ngrok.com/get-started/your-authtoken

## Configuration

1. **Add your ngrok token to `.env`**:
   ```bash
   # In backend/.env file
   NGROK_AUTHTOKEN=your_token_here
   NGROK_ENABLED=True
   ```

2. **Configure ngrok settings** (optional):
   Edit `ngrok.yml` to customize:
   - Custom domain (paid plan)
   - Basic authentication
   - IP restrictions
   - Custom subdomain (paid plan)

## Usage

### Option 1: Local Development with ngrok

**Windows (PowerShell):**
```powershell
cd backend
.\start-with-ngrok.ps1
```

**Linux/Mac/Git Bash:**
```bash
cd backend
./start-with-ngrok.sh
```

This will:
1. Set up the virtual environment
2. Install dependencies
3. Run database migrations
4. Start ngrok tunnel
5. Display your public URL
6. Start the API server

Example output:
```
========================================
✓ ngrok tunnel established!
========================================

Public URL:  https://abc123.ngrok.io
Local URL:   http://localhost:8000
API Docs:    https://abc123.ngrok.io/docs
ngrok Web:   http://localhost:4040

========================================
```

### Option 2: Podman/Docker with ngrok

**Windows (PowerShell):**
```powershell
cd backend
.\start-podman-ngrok.ps1
```

**Linux/Mac/Git Bash:**
```bash
cd backend
./start-podman-ngrok.sh
```

This will:
1. Start PostgreSQL database
2. Start the API container
3. Start ngrok container
4. Display your public URL

**Useful commands:**
```bash
# View logs
./start-podman-ngrok.sh --logs

# Stop everything
./start-podman-ngrok.sh --down

# Rebuild containers
./start-podman-ngrok.sh --build
```

## ngrok Dashboard

Access the ngrok web interface at: **http://localhost:4040**

Features:
- View all active tunnels
- Inspect HTTP requests/responses
- Replay requests
- View connection stats

## Important Notes

### Free Plan Limitations
- Random URL each time (e.g., `https://abc123.ngrok.io`)
- Session timeout after inactivity
- Limited connections per minute
- No custom domains

### Paid Plan Features
- **Custom domains**: Use your own domain
- **Reserved subdomains**: Get a permanent subdomain
- **More connections**: Higher rate limits
- **No session timeout**: Persistent tunnels
- **IP whitelisting**: Restrict access

### Security Considerations

1. **Don't expose sensitive data** on the free plan
2. **Use authentication** for production-like testing:
   ```yaml
   # In ngrok.yml
   auth: "user:password"
   ```

3. **IP restrictions** (paid plan):
   ```yaml
   # In ngrok.yml
   ip_restriction:
     allow_cidrs:
       - "1.2.3.4/32"
   ```

4. **HTTPS only**: ngrok provides automatic HTTPS

### CORS Configuration

If you need to access the API from a web app, update CORS settings in `.env`:
```env
CORS_ORIGINS=["https://your-frontend.com","https://abc123.ngrok.io"]
```

Or allow all origins (development only):
```python
# In app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Not recommended for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Troubleshooting

### "ngrok command not found"
- Make sure ngrok is installed and in your PATH
- Restart your terminal after installation

### "authtoken is not set"
- Check that `NGROK_AUTHTOKEN` is set in `.env`
- Make sure there are no spaces around the `=` sign

### "tunnel session failed"
- Verify your authtoken is correct
- Check your internet connection
- Try restarting ngrok

### "502 Bad Gateway"
- Make sure your API server is running
- Check that it's listening on port 8000
- Verify the database is accessible

### "Could not retrieve ngrok URL"
- Wait a few seconds and check http://localhost:4040
- The tunnel might still be starting up
- Check ngrok logs: `docker compose -f docker-compose-ngrok.yml logs ngrok`

## Alternatives to ngrok

If ngrok doesn't meet your needs, consider:
- **localhost.run**: Free, no account needed
- **Cloudflare Tunnel**: Free, requires account
- **serveo.net**: Free SSH tunneling
- **Tailscale**: Private network, free for personal use
- **localtunnel**: Free, open source

## Production Deployment

For production, don't use ngrok. Instead:
- Deploy to a cloud provider (AWS, Azure, GCP, etc.)
- Use a proper domain with SSL
- Set up a reverse proxy (nginx, Traefik)
- Use environment-specific configurations
