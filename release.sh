#!/bin/bash

# Release script for STT/TTS Bridge Home Assistant integration
# Usage: ./release.sh <version> [release-notes]
# Example: ./release.sh 0.1.7 "Fixed STT audio header compatibility"

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

if [ -z "$1" ]; then
    echo -e "${RED}Error: Version number required${NC}"
    echo "Usage: ./release.sh <version> [release-notes]"
    echo "Example: ./release.sh 0.1.7 'Fixed STT audio header compatibility'"
    exit 1
fi

VERSION="$1"
RELEASE_NOTES="${2:-Release v$VERSION}"

echo -e "${YELLOW}Creating release v$VERSION${NC}"
echo "Release notes: $RELEASE_NOTES"
echo ""

# Check if there are uncommitted changes
if [[ -n $(git status -s) ]]; then
    echo -e "${YELLOW}Uncommitted changes found. Committing...${NC}"
    git add -A
    git commit -m "$RELEASE_NOTES"
else
    echo -e "${GREEN}No uncommitted changes${NC}"
fi

# Push to remote
echo -e "${YELLOW}Pushing to remote...${NC}"
git push

# Create and push tag
echo -e "${YELLOW}Creating tag v$VERSION...${NC}"
git tag -a "v$VERSION" -m "$RELEASE_NOTES"
git push origin "v$VERSION"

# Create GitHub release
echo -e "${YELLOW}Creating GitHub release...${NC}"
gh release create "v$VERSION" \
    --title "v$VERSION" \
    --notes "$RELEASE_NOTES"

echo -e "${GREEN}✓ Release v$VERSION created successfully!${NC}"
echo -e "${GREEN}✓ Available at: https://github.com/daydy16/ha-local-macos-tts-stt/releases/tag/v$VERSION${NC}"
