# GitHub Actions Setup Guide

This guide will help you set up GitHub Actions for automated CI/CD deployment of your Dynamic AI Chatbot project.

## 🚀 Quick Setup

### 1. Repository Setup

Your GitHub Actions workflows are already configured in `.github/workflows/`. The main workflows are:

- **`ci.yml`** - Continuous Integration (testing, linting, security scans)
- **`deploy.yml`** - Automated deployment to multiple platforms
- **`release.yml`** - Release management and versioning

### 2. Required Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions, and add these secrets:

#### Essential Secrets
```bash
# Database
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/chatbot_db

# AI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# Security
JWT_SECRET_KEY=your-super-secret-jwt-key-minimum-32-characters
```

#### Platform-Specific Secrets (choose your deployment platform)

**For Vercel Deployment:**
```bash
VERCEL_TOKEN=your-vercel-token
VERCEL_ORG_ID=your-vercel-org-id
VERCEL_PROJECT_ID=your-vercel-project-id
```

**For Railway Deployment:**
```bash
RAILWAY_TOKEN=your-railway-token
```

**For Render Deployment:**
```bash
RENDER_API_KEY=your-render-api-key
RENDER_SERVICE_ID=your-render-service-id
```

#### Optional Secrets
```bash
# Notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/your/slack/webhook

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

## 🔧 Platform-Specific Setup

### Vercel Setup

1. **Install Vercel CLI locally:**
   ```bash
   npm install -g vercel
   ```

2. **Create Vercel project:**
   ```bash
   vercel link
   ```

3. **Get your Vercel credentials:**
   ```bash
   # Get token from: https://vercel.com/account/tokens
   # Get org and project IDs from: vercel project ls
   ```

4. **Add secrets to GitHub repository**

### Railway Setup

1. **Create Railway project:**
   - Go to [Railway](https://railway.app)
   - Connect your GitHub repository
   - Create a new project

2. **Get Railway token:**
   ```bash
   # Install Railway CLI
   curl -sSL https://railway.app/install.sh | sh
   
   # Login and get token
   railway login
   railway tokens
   ```

3. **Add `RAILWAY_TOKEN` to GitHub secrets**

### Render Setup

1. **Create Render service:**
   - Go to [Render](https://render.com)
   - Connect your GitHub repository
   - Create a new Web Service

2. **Get API credentials:**
   - Go to Account Settings → API Keys
   - Create a new API key
   - Get your service ID from the service dashboard

3. **Add secrets to GitHub repository**

## 📁 Workflow Structure

### CI Workflow (`ci.yml`)
- **Triggers:** Push to any branch, PRs to main/develop
- **Jobs:**
  - Code linting and formatting (Black, flake8, ESLint)
  - Multi-platform testing (Ubuntu, Windows, macOS)
  - Docker build testing
  - Performance testing
  - Security scanning

### Deploy Workflow (`deploy.yml`)
- **Triggers:** Push to main branch
- **Jobs:**
  - Run tests
  - Build and push Docker image
  - Deploy to Railway/Vercel/Render
  - Security scanning
  - Slack notifications

### Release Workflow (`release.yml`)
- **Triggers:** New git tags (v*)
- **Jobs:**
  - Create GitHub release
  - Generate changelog
  - Build release packages
  - Deploy to production

## 🎯 Usage Examples

### Creating a Release
```bash
# Create and push a new tag
git tag v1.0.0
git push origin v1.0.0

# This triggers the release workflow automatically
```

### Manual Deployment
```bash
# Push to main branch triggers automatic deployment
git push origin main
```

### Testing Changes
```bash
# Create a feature branch
git checkout -b feature/new-feature

# Push triggers CI tests
git push origin feature/new-feature

# Create PR to main triggers full CI pipeline
```

## 🔍 Monitoring Deployments

### GitHub Actions Dashboard
- Go to your repository → Actions tab
- Monitor workflow runs in real-time
- View logs and debug failed deployments

### Deployment Status
- Check deployment status in the Actions tab
- Successful deployments will show green checkmarks
- Failed deployments will show red X marks with error logs

### Notifications
If you set up Slack webhook, you'll receive notifications for:
- Successful deployments
- Failed deployments
- Security scan results

## 🛠 Customization

### Adding New Deployment Targets
Edit `.github/workflows/deploy.yml` and add new job:

```yaml
deploy-to-custom:
  needs: test
  runs-on: ubuntu-latest
  if: github.ref == 'refs/heads/main'
  
  steps:
  - name: Deploy to Custom Platform
    run: |
      # Add your deployment commands here
      echo "Deploying to custom platform..."
```

### Modifying Test Suite
Edit `.github/workflows/ci.yml` to customize:
- Test matrix (Python versions, OS)
- Linting rules
- Security scan configurations

### Environment-Specific Deployments
Create separate workflows for different environments:
- `deploy-staging.yml` for staging environment
- `deploy-production.yml` for production environment

## 🔒 Security Best Practices

1. **Never commit secrets** - Always use GitHub Secrets
2. **Use least privilege** - Grant minimal required permissions
3. **Regular updates** - Dependabot is configured for automatic updates
4. **Security scanning** - Trivy and safety checks are included
5. **Code quality** - Linting and formatting are enforced

## 📊 Badge Integration

Add these badges to your README.md:

```markdown
![CI](https://github.com/neslang-05/dynamic_ai_chatbot/workflows/CI%2FCD%20Pipeline/badge.svg)
![Deploy](https://github.com/neslang-05/dynamic_ai_chatbot/workflows/Deploy%20Dynamic%20AI%20Chatbot/badge.svg)
![Security](https://github.com/neslang-05/dynamic_ai_chatbot/workflows/Security%20Scan/badge.svg)
```

## 🎉 You're Ready!

Once you've added the required secrets, your GitHub Actions will automatically:

1. **Test** every push and pull request
2. **Deploy** when you push to main
3. **Create releases** when you tag versions
4. **Monitor security** with automated scans
5. **Notify** you of deployment status

Your Dynamic AI Chatbot is now ready for professional CI/CD! 🚀