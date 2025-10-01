#!/bin/bash
# AI Image Chat - Development Environment Setup Script
#
# This script sets up the complete development environment including:
# - Development dependencies (testing, linting, formatting tools)
# - Pre-commit hooks for automated code quality checks
# - Initial formatting baseline
#
# Usage:
#   bash scripts/setup-dev.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print header
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}AI Image Chat - Development Setup${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "requirements-dev.txt" ]; then
    echo -e "${RED}❌ Error: requirements-dev.txt not found${NC}"
    echo -e "${RED}   Please run this script from the project root directory${NC}"
    exit 1
fi

# Step 1: Install development dependencies
echo -e "${YELLOW}📦 Step 1/4: Installing development dependencies...${NC}"
pip install -r requirements-dev.txt
echo -e "${GREEN}✓ Development dependencies installed${NC}"
echo ""

# Step 2: Install pre-commit hooks
echo -e "${YELLOW}🪝 Step 2/4: Installing pre-commit hooks...${NC}"
pre-commit install
echo -e "${GREEN}✓ Pre-commit hooks installed${NC}"
echo ""

# Step 3: Run pre-commit on all files (establish baseline)
echo -e "${YELLOW}🎨 Step 3/4: Running code formatting and checks...${NC}"
echo -e "${BLUE}   This may take a few moments on first run...${NC}"

# Run pre-commit but don't fail if it makes changes
if pre-commit run --all-files; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
else
    echo -e "${YELLOW}⚠️  Pre-commit made some formatting changes${NC}"
    echo -e "${YELLOW}   This is normal for the first run${NC}"
    echo -e "${YELLOW}   Files have been automatically formatted${NC}"
fi
echo ""

# Step 4: Verify setup
echo -e "${YELLOW}🔍 Step 4/4: Verifying setup...${NC}"

# Check if pre-commit is installed
if command -v pre-commit &> /dev/null; then
    echo -e "${GREEN}✓ pre-commit is available${NC}"
else
    echo -e "${RED}❌ pre-commit not found in PATH${NC}"
    exit 1
fi

# Check if git hooks are installed
if [ -f ".git/hooks/pre-commit" ]; then
    echo -e "${GREEN}✓ Git pre-commit hook is installed${NC}"
else
    echo -e "${YELLOW}⚠️  Git pre-commit hook not found (not a git repository?)${NC}"
fi

echo ""
echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}✅ Development environment setup complete!${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo ""
echo -e "  1. ${BLUE}Make your code changes${NC}"
echo -e "     - Edit files in core/, utils/, or other directories"
echo ""
echo -e "  2. ${BLUE}Test your changes${NC}"
echo -e "     make test             # Run tests"
echo -e "     make coverage         # Run tests with coverage"
echo ""
echo -e "  3. ${BLUE}Format and lint (optional - hooks do this automatically)${NC}"
echo -e "     make format           # Format with Black"
echo -e "     make lint             # Lint with Ruff"
echo -e "     make check            # Run all checks"
echo ""
echo -e "  4. ${BLUE}Commit your changes${NC}"
echo -e "     git add ."
echo -e "     git commit -m \"Your commit message\""
echo -e "     ${GREEN}→ Pre-commit hooks will run automatically!${NC}"
echo ""
echo -e "${YELLOW}Tips:${NC}"
echo -e "  - Pre-commit hooks run automatically on ${BLUE}git commit${NC}"
echo -e "  - To skip hooks: ${BLUE}git commit --no-verify${NC} (not recommended)"
echo -e "  - Run hooks manually: ${BLUE}pre-commit run --all-files${NC}"
echo -e "  - Update hooks: ${BLUE}pre-commit autoupdate${NC}"
echo ""
echo -e "See ${BLUE}CONTRIBUTING.md${NC} for complete documentation."
echo ""
