#!/bin/bash

echo "PostgreSQL Installation Script for Mac"
echo "======================================"
echo ""
echo "This script will guide you through installing PostgreSQL on your Mac."
echo ""

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew is not installed. Please install it first:"
    echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

echo "Option 1: Install via Homebrew (Recommended)"
echo "---------------------------------------------"
echo "Run these commands in your terminal:"
echo ""
echo "# Fix Homebrew permissions (requires password):"
echo "sudo chown -R \$(whoami) /usr/local/share/zsh /usr/local/share/zsh/site-functions"
echo "chmod u+w /usr/local/share/zsh /usr/local/share/zsh/site-functions"
echo ""
echo "# Install PostgreSQL:"
echo "brew install postgresql@16"
echo ""
echo "# Start PostgreSQL service:"
echo "brew services start postgresql@16"
echo ""
echo "# Add PostgreSQL to PATH:"
echo "echo 'export PATH=\"/usr/local/opt/postgresql@16/bin:\$PATH\"' >> ~/.zshrc"
echo "source ~/.zshrc"
echo ""
echo "# Create database for ROI Calculator:"
echo "createdb roi_calculator"
echo ""

echo "Option 2: Install via Postgres.app (GUI Alternative)"
echo "----------------------------------------------------"
echo "1. Download from: https://postgresapp.com/downloads.html"
echo "2. Move to Applications folder"
echo "3. Launch Postgres.app"
echo "4. Click 'Initialize' to create a new server"
echo "5. Add to PATH by running:"
echo "   sudo mkdir -p /etc/paths.d && echo /Applications/Postgres.app/Contents/Versions/latest/bin | sudo tee /etc/paths.d/postgresapp"
echo ""

echo "After installation, verify with:"
echo "psql --version"
echo ""
echo "Then return here and run:"
echo "python setup_database.py"