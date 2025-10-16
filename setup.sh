#!/bin/bash

# Pulseway MCP Server Setup Script
# This script helps you set up the Pulseway MCP Server quickly

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}==================================${NC}"
echo -e "${GREEN}Pulseway MCP Server Setup${NC}"
echo -e "${GREEN}==================================${NC}"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}uv is not installed. Installing uv...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    echo -e "${GREEN}✓ uv installed successfully${NC}"
else
    echo -e "${GREEN}✓ uv is already installed${NC}"
fi

# Check Python version
echo ""
echo -e "${YELLOW}Checking Python version...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"
else
    echo -e "${RED}✗ Python 3 not found. Please install Python 3.10 or higher.${NC}"
    exit 1
fi

# Install dependencies
echo ""
echo -e "${YELLOW}Installing dependencies...${NC}"
uv pip install -e ".[dev]"
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create .env file if it doesn't exist
echo ""
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}⚠ Please edit .env and add your Pulseway credentials${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Check if credentials are configured
echo ""
if grep -q "PULSEWAY_SERVER_URL=$" .env || grep -q "PULSEWAY_TOKEN_ID=$" .env; then
    echo -e "${YELLOW}⚠ Warning: Environment variables not configured${NC}"
    echo ""
    echo "Please edit .env and add your Pulseway credentials:"
    echo "  1. Open .env in your editor"
    echo "  2. Set PULSEWAY_SERVER_URL (e.g., https://your-instance.pulseway.com)"
    echo "  3. Set PULSEWAY_TOKEN_ID (from Pulseway Admin)"
    echo "  4. Set PULSEWAY_TOKEN_SECRET (from Pulseway Admin)"
    echo ""
    echo "To obtain credentials:"
    echo "  1. Log in to Pulseway"
    echo "  2. Go to Administration → Configuration → API Access"
    echo "  3. Create a new token"
    echo ""
else
    echo -e "${GREEN}✓ Environment variables configured${NC}"
fi

# Run tests
echo ""
echo -e "${YELLOW}Running tests...${NC}"
if uv run pytest -q; then
    echo -e "${GREEN}✓ All tests passed${NC}"
else
    echo -e "${YELLOW}⚠ Some tests failed (this is normal if credentials aren't configured)${NC}"
fi

# Success message
echo ""
echo -e "${GREEN}==================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}==================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Configure your credentials in .env"
echo "  2. Test the server: make run"
echo "  3. Configure Claude Desktop (see README.md)"
echo ""
echo "For more information, see:"
echo "  - README.md for usage instructions"
echo "  - CONTRIBUTING.md for development guidelines"
echo ""
echo "Run 'make help' to see available commands"
