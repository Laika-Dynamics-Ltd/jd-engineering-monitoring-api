# 🚀 GitHub Automation Setup Guide

## Complete Issues + Actions + Projects Integration

This guide will help you set up the complete GitHub automation system for the JD Engineering Monitoring API project.

## 📋 Prerequisites

1. **GitHub Repository Access**: You need admin access to the repository
2. **GitHub Personal Access Token**: Create one with these permissions:
   - `repo` (full control)
   - `workflow` (update GitHub Actions)
   - `project` (manage projects)

## 🏗️ Setup Instructions

### Step 1: Create GitHub Project (Manual - One Time)

1. Go to your repository: https://github.com/Laika-Dynamics-Lt/jd-engineering-monitoring-api
2. Click on "Projects" tab
3. Click "New project" → Choose "Board" template
4. Name it: "JD Engineering Roadmap"
5. Create these columns:
   - 📋 Backlog
   - 🚧 In Progress
   - ✅ Done

### Step 2: Run Initial Setup

```bash
# Clone the repository
git clone https://github.com/Laika-Dynamics-Lt/jd-engineering-monitoring-api.git
cd jd-engineering-monitoring-api

# Create a new branch for automation setup
git checkout -b setup/github-automation

# Commit the automation files
git add .github/
git commit -m "feat: add GitHub automation workflows and issue templates"
git push origin setup/github-automation
```

### Step 3: Create Labels and Issues

1. Go to Actions tab in your repository
2. Find "Create Roadmap Issues" workflow
3. Click "Run workflow" → "Run workflow"
4. This will:
   - Create all priority and category labels
   - Generate 10 prioritized roadmap issues

### Step 4: Enable Automation

The automation is now active! Here's how it works:

## 🔄 Development Workflow

### Starting Work on an Issue

```bash
# Pick an issue (e.g., Issue #5)
git checkout -b feature/analytics-dashboard-5

# Make your changes
# ...

# Commit with keyword to move issue to "In Progress"
git commit -m "wip: implementing analytics dashboard #5"
git push origin feature/analytics-dashboard-5
```

### During Development

```bash
# Regular commits
git commit -m "feat: add cost calculator to analytics #5"
git commit -m "fix: correct chart rendering issue #5"
```

### Completing Work

```bash
# Final commit to close issue
git commit -m "close: analytics dashboard complete #5"
git push origin feature/analytics-dashboard-5

# Create PR
# The PR will automatically link to the issue
```

## ⚙️ Automation Features

### Commit Keywords

| Keyword | Action | Example |
|---------|--------|---------|
| `wip:` | Move to "In Progress" | `git commit -m "wip: working on auth #6"` |
| `feat:` | Move to "In Progress" | `git commit -m "feat: add login page #6"` |
| `fix:` | Move to "In Progress" | `git commit -m "fix: resolve timeout #1"` |
| `close:` | Move to "Done" & close issue | `git commit -m "close: auth complete #6"` |
| `resolve:` | Move to "Done" & close issue | `git commit -m "resolve: fixed timeout #1"` |

### Auto-labeling

New issues are automatically labeled based on content:
- Mentions "frontend", "UI", "dashboard" → `frontend` label
- Mentions "backend", "API", "server" → `backend` label
- Mentions "mobile", "tablet", "Android" → `mobile` label
- And more...

### Project Sync

- New issues automatically added to "Backlog"
- Critical issues may start in "In Progress"
- Closed issues move to "Done"

## 📊 Monitoring Progress

### View Project Board
1. Go to Projects tab
2. Click on "JD Engineering Roadmap"
3. See visual progress of all issues

### Track Metrics
- Issues by priority
- Completion rate
- Time in each column
- Velocity trends

## 🎯 Priority Guidelines

### 🔴 CRITICAL (Fix immediately)
- Production blocking issues
- Data loss risks
- Security vulnerabilities

### 🟠 HIGH (This week)
- Major feature gaps
- Performance issues
- UX problems

### 🟡 MEDIUM (This month)
- Enhancement requests
- Technical debt
- Minor bugs

### 🟢 LOW (When possible)
- Nice-to-have features
- Cosmetic improvements
- Future considerations

## 🚨 Troubleshooting

### Issues not syncing to project?
- Check Actions tab for workflow runs
- Ensure labels are correct
- Verify project permissions

### Commits not updating issues?
- Use exact keyword format (e.g., `fix:` not `Fix:`)
- Include issue number with # (e.g., `#5`)
- Push commits to GitHub

### Workflow failures?
- Check Actions tab for error logs
- Verify GitHub token permissions
- Ensure branch protections allow updates

## 📈 Best Practices

1. **One issue per feature/bug**
2. **Clear, descriptive titles**
3. **Always reference issue numbers in commits**
4. **Use appropriate priority labels**
5. **Keep issues updated with progress**
6. **Close issues via commits for automation**

## 🔗 Quick Links

- [Create New Issue](https://github.com/Laika-Dynamics-Lt/jd-engineering-monitoring-api/issues/new)
- [View Project Board](https://github.com/Laika-Dynamics-Lt/jd-engineering-monitoring-api/projects)
- [Actions Dashboard](https://github.com/Laika-Dynamics-Lt/jd-engineering-monitoring-api/actions)

## 💡 Advanced Usage

### Custom Issue Templates

Edit `.github/roadmap-issues.json` to customize default issues.

### Workflow Modifications

Edit workflows in `.github/workflows/` to change automation behavior.

### Additional Integrations

Consider adding:
- Slack notifications
- Deploy previews
- Test coverage reports
- Performance benchmarks

---

**Need help?** Open an issue with the `help` label! 