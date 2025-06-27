# 🚀 GITHUB AUTOMATION META PROMPT
## Complete Issues + Actions + Projects Integration

<!-- 
SETUP INSTRUCTIONS:
1. Add your project details at the top
2. Paste this entire prompt into Cursor IDE
3. Ask AI to "Set up complete GitHub automation for this project"
-->

## 📋 PROJECT CONFIGURATION
```
REPO_OWNER: Laika-Dynamics-Lt
REPO_NAME: jd-engineering-monitoring-api
PROJECT_NUMBER: [WILL_BE_AUTO_GENERATED]
```

---

## 🎯 AUTOMATION REQUIREMENTS

I need you to set up **complete GitHub automation** for this project with the following architecture:

### 🔧 **Core Components**
1. **GitHub Issues** - Prioritized roadmap with smart labeling
2. **GitHub Actions** - Automated workflows and project sync
3. **Repository Projects** - Visual project management (NOT organization-level)

### 📊 **Project Structure**
- **Repository-level GitHub Project** (simpler, faster, more portable)
- **Automatic issue-to-project sync**
- **Commit-based workflow automation**
- **Smart keyword detection** (fix, close, wip, etc.)

---

## 🏗️ IMPLEMENTATION CHECKLIST

### **Phase 1: Project Setup**
- [ ] Create repository-level GitHub Project
- [ ] Set up project columns: "📋 Backlog", "🚧 In Progress", "✅ Done"
- [ ] Configure project automation rules

### **Phase 2: Issue System**
- [ ] Create comprehensive label system (priority, technology, business)
- [ ] Generate 10 prioritized roadmap issues
- [ ] Auto-assign issues to project

### **Phase 3: GitHub Actions**
- [ ] Workflow: Auto-create issues on push
- [ ] Workflow: Project sync automation
- [ ] Workflow: Commit-based issue management
- [ ] Workflow: Project automation triggers

### **Phase 4: Development Workflow**
- [ ] Commit format: `fix: description #issue_number`
- [ ] Branch naming: `feature/description-issue_number`
- [ ] Auto-move cards based on commits

---

## 📝 ISSUE TEMPLATE STRUCTURE

Create issues with this priority system:
- 🔴 **CRITICAL** (1-2 issues) - Blocking production
- 🟠 **HIGH** (3-4 issues) - Important for success
- 🟡 **MEDIUM** (3-4 issues) - Should be addressed
- 🟢 **LOW** (2-3 issues) - Nice to have

Each issue should include:
- **Priority level and estimate**
- **Problem description**
- **Acceptance criteria**
- **Definition of done**
- **Relevant file paths**

---

## ⚙️ GITHUB ACTIONS WORKFLOWS

### **Required Workflows:**
1. `.github/workflows/create-issues.yml` - Auto-generate roadmap
2. `.github/workflows/project-automation.yml` - Commit-based automation
3. `.github/workflows/issue-sync.yml` - Project synchronization

### **Automation Features:**
- **Commit triggers**: `git commit -m "fix: navigation issue #1"` → moves to "In Progress"
- **Close triggers**: `git commit -m "close: navigation complete #1"` → moves to "Done"
- **WIP triggers**: `git commit -m "wip: working on search #5"` → moves to "In Progress"

---

## 🎨 LABEL SYSTEM

### **Priority Labels:**
- `priority-critical` (🔴 Red)
- `priority-high` (🟠 Orange) 
- `priority-medium` (🟡 Yellow)
- `priority-low` (🟢 Green)

### **Technology Labels:**
- `frontend`, `backend`, `mobile`, `api`
- `ui/ux`, `performance`, `security`
- `database`, `deployment`, `testing`

### **Business Labels:**
- `monetization`, `user-experience`, `analytics`
- `marketing`, `seo`, `compliance`

---

## 🔄 DEVELOPMENT WORKFLOW

### **Starting Work:**
```bash
git checkout -b feature/search-enhancement-5
git commit -m "wip: implementing search filters #5"
```

### **During Development:**
```bash
git commit -m "feat: add search autocomplete #5"
git commit -m "fix: search performance issue #5"
```

### **Completing Work:**
```bash
git commit -m "close: search enhancement complete #5"
git push origin feature/search-enhancement-5
```

---

## 📊 SUCCESS METRICS

### **Automation Goals:**
- ✅ Zero manual project management
- ✅ Issues auto-sync with project
- ✅ Commit-driven workflow
- ✅ Complete development visibility
- ✅ Business-focused prioritization

### **Expected Outcome:**
- **Issues**: Comprehensive roadmap with clear priorities
- **Actions**: Fully automated project management
- **Projects**: Visual progress tracking with zero manual updates
- **Workflow**: Seamless development experience

---

## 🚀 DEPLOYMENT INSTRUCTIONS

### **Step 1: Initial Setup**
1. Ask AI: "Set up complete GitHub automation using repository-level projects"
2. Provide GitHub token when prompted
3. Verify all workflows are created

### **Step 2: Create Issues**
1. Run issue creation script
2. Verify issues appear in repository project
3. Test commit-based automation

### **Step 3: Start Development**
1. Pick highest priority issue
2. Create feature branch
3. Use commit-based workflow

---

## 💡 CUSTOMIZATION NOTES

### **For Different Project Types:**
- **SaaS Projects**: Focus on monetization and user experience
- **Open Source**: Emphasize community and documentation
- **Enterprise**: Prioritize security and compliance
- **Startups**: Balance features with technical debt

### **Scaling Options:**
- **Single Developer**: Use all automation features
- **Small Team**: Add team-specific labels and workflows
- **Large Team**: Consider organization-level projects later

---

## 🎯 FINAL REQUEST

Please implement this complete GitHub automation system using **repository-level projects** for maximum portability and simplicity. Create all necessary files, workflows, and scripts to achieve seamless integration between Issues, Actions, and Projects.

**Focus on:**
- Repository-level GitHub Projects (not organization-level)
- Complete automation with zero manual project management
- Business-focused issue prioritization
- Commit-driven workflow
- Universal compatibility across all project types

**Start with:** "I'll set up complete GitHub automation using repository-level projects for maximum portability..." 