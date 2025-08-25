# 🚀 Production Deployment

Simple one-time deployment to DigitalOcean droplet with GitHub Actions.

## Prerequisites

- DigitalOcean droplet with Ubuntu
- SSH key access to droplet
- GitHub repository with Actions enabled

## 1. Setup Droplet (One-time)

SSH into your droplet and run:

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh
systemctl start docker
systemctl enable docker

# Create directories
mkdir -p /app/data /app/logs
chmod 755 /app/data /app/logs

# Setup firewall
ufw allow ssh
ufw allow 3000/tcp
ufw --force enable

echo "✅ Droplet ready for deployment"
```

## 2. Configure GitHub Secrets

Run the secure setup script:

```bash
./scripts/setup-secrets.sh
```

This will configure all required secrets using GitHub CLI:
- `DO_PAT_TOKEN` - DigitalOcean PAT token  
- `DO_SSH_PRIVATE_KEY` - SSH private key for droplet access
- `DROPLET_IP` - Your droplet IP address
- `GITHUB_PERSONAL_ACCESS_TOKEN` - GitHub PAT with repo scope
- `GITHUB_WEBHOOK_SECRET` - Webhook verification secret
- `GITHUB_OWNER` - Your GitHub username
- `GITHUB_REPO` - Repository name  
- `OPENAI_API_KEY` - OpenAI API key

## 3. Deploy

Push to main branch:

```bash
git push origin main
```

GitHub Actions will automatically:
- Build Docker image
- Push to `registry.digitalocean.com/synthetic/ai-coding-agent:latest`
- Pull image on droplet from registry
- Start the service
- Verify health

## 4. Configure GitHub Webhook

After deployment, set up webhook in your GitHub repo:

- URL: `http://YOUR_DROPLET_IP:3000/webhook`
- Content type: `application/json`
- Secret: Same as `GITHUB_WEBHOOK_SECRET`
- Events: Issues only

## 5. Test

Create a GitHub issue with a coding task and watch the agent work!

---

**Your AI Coding Agent is now live in production! 🎉**