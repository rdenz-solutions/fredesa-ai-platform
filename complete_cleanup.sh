#!/bin/bash
# Complete FreDeSa repository cleanup and commit

cd "/Users/delchaplin/Project Files/fredesa-ai-platform"

echo "🔍 Checking current state..."
echo ""

# Count root files
ROOT_FILES=$(find . -maxdepth 1 -type f ! -name ".*" | wc -l | xargs)
echo "Root files (non-hidden): $ROOT_FILES"
find . -maxdepth 1 -type f ! -name ".*" -exec basename {} \;
echo ""

# Perform cleanup operations
echo "🧹 Performing cleanup..."

# Remove .DS_Store
if [ -f .DS_Store ]; then
    rm .DS_Store
    echo "✅ Removed .DS_Store"
fi

# Remove verify script
if [ -f verify_cleanup.py ]; then
    rm verify_cleanup.py
    echo "✅ Removed verify_cleanup.py"
fi

# Create directories
mkdir -p config/env
mkdir -p archive/scripts

# Move files
if [ -f .env.production ]; then
    mv .env.production config/env/production.env
    echo "✅ Moved .env.production → config/env/production.env"
fi

if [ -f .env.test ]; then
    mv .env.test config/env/test.env
    echo "✅ Moved .env.test → config/env/test.env"
fi

if [ -f reorganize.sh ]; then
    mv reorganize.sh archive/scripts/
    echo "✅ Moved reorganize.sh → archive/scripts/"
fi

echo ""
echo "📊 Final state:"
ROOT_FILES=$(find . -maxdepth 1 -type f ! -name ".*" ! -name "complete_cleanup.sh" | wc -l | xargs)
echo "Root files: $ROOT_FILES"
find . -maxdepth 1 -type f ! -name ".*" ! -name "complete_cleanup.sh" -exec basename {} \;

echo ""
echo "📝 Staging and committing changes..."
git add -A
git commit -m "feat: Complete repository cleanup - reduce root files

- Moved .env.production → config/env/production.env
- Moved .env.test → config/env/test.env  
- Archived reorganize.sh → archive/scripts/
- Removed .DS_Store and temporary scripts
- Target: Keep only 4 root MD/config files

Aligns with REPOSITORY_STRUCTURE.md standards"

echo ""
echo "✅ Cleanup complete!"
echo "Run: rm complete_cleanup.sh"
