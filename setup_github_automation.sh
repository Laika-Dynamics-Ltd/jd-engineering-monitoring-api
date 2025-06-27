#!/bin/bash

# JD Engineering Monitoring API - GitHub Automation Setup Script
# This script helps set up the complete GitHub automation system

echo "🚀 JD Engineering GitHub Automation Setup"
echo "========================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo -e "${RED}❌ Error: Not in the jd-engineering-monitoring-api directory${NC}"
    echo "Please run this script from the project root directory"
    exit 1
fi

echo -e "${BLUE}📋 Prerequisites Check${NC}"
echo "----------------------"

# Check for git
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git is not installed${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Git is installed${NC}"
fi

# Check for GitHub CLI (optional but helpful)
if command -v gh &> /dev/null; then
    echo -e "${GREEN}✅ GitHub CLI is installed (optional)${NC}"
    GH_CLI=true
else
    echo -e "${YELLOW}⚠️  GitHub CLI not installed (optional)${NC}"
    GH_CLI=false
fi

echo ""
echo -e "${BLUE}🏗️  Setting Up GitHub Automation${NC}"
echo "--------------------------------"

# Create branch for automation setup
echo -e "${YELLOW}Creating setup branch...${NC}"
git checkout -b setup/github-automation 2>/dev/null || {
    echo -e "${YELLOW}Branch already exists, switching to it...${NC}"
    git checkout setup/github-automation
}

# Stage GitHub automation files
echo -e "${YELLOW}Staging automation files...${NC}"
git add .github/

# Show what will be committed
echo ""
echo -e "${BLUE}📝 Files to be committed:${NC}"
git status --short .github/

echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "-------------"
echo "1. Commit and push these changes:"
echo -e "   ${GREEN}git commit -m \"feat: add GitHub automation workflows and issue templates\"${NC}"
echo -e "   ${GREEN}git push origin setup/github-automation${NC}"
echo ""
echo "2. Create a Pull Request to merge these changes"
echo ""
echo "3. After merging, go to the Actions tab and run:"
echo "   - 'Create Roadmap Issues' workflow"
echo ""
echo "4. Create a GitHub Project manually:"
echo "   - Go to Projects tab"
echo "   - Click 'New project' → 'Board'"
echo "   - Name: 'JD Engineering Roadmap'"
echo "   - Add columns: 📋 Backlog, 🚧 In Progress, ✅ Done"
echo ""

if [ "$GH_CLI" = true ]; then
    echo -e "${BLUE}🚀 Quick Commands (using GitHub CLI):${NC}"
    echo "-------------------------------------"
    echo "Create PR:"
    echo -e "   ${GREEN}gh pr create --title \"feat: add GitHub automation\" --body \"Implements complete GitHub automation with Issues, Actions, and Projects integration\"${NC}"
    echo ""
    echo "After merge, trigger workflow:"
    echo -e "   ${GREEN}gh workflow run create-issues.yml${NC}"
    echo ""
fi

echo -e "${BLUE}📖 Documentation:${NC}"
echo "----------------"
echo "Full setup guide: .github/GITHUB_AUTOMATION_SETUP.md"
echo ""

echo -e "${GREEN}✅ GitHub automation files are ready!${NC}"
echo ""
echo -e "${YELLOW}⚡ Pro tip: Use commit keywords to automate issue management:${NC}"
echo "   - 'wip: message #123' → moves issue to In Progress"
echo "   - 'fix: message #123' → moves issue to In Progress"
echo "   - 'close: message #123' → closes issue and moves to Done"
echo ""

# Make the script executable
chmod +x setup_github_automation.sh

echo -e "${BLUE}🎉 Setup complete! Follow the next steps above.${NC}" 