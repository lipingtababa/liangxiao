#!/bin/bash

echo "================================================"
echo "🎯 BLACK BOX E2E TEST FOR SYNTHETICCODINGTEAM"
echo "================================================"
echo ""
echo "This test will:"
echo "1. Start the SCT service as a real server"
echo "2. Send a simulated GitHub webhook"
echo "3. Wait for a PR to be created on GitHub"
echo "4. Validate the PR submission"
echo ""

# Check for required environment variables
if [ -z "$GITHUB_TOKEN" ] && [ -z "$GITHUB_PERSONAL_ACCESS_TOKEN" ]; then
    echo "❌ Error: GITHUB_TOKEN or GITHUB_PERSONAL_ACCESS_TOKEN must be set"
    exit 1
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️ Warning: OPENAI_API_KEY not set - SCT may not work properly"
fi

# Run the black box test
echo "🚀 Starting black box test..."
python test_blackbox_e2e.py

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ BLACK BOX TEST PASSED!"
    echo "The SCT system successfully:"
    echo "  - Started as a service"
    echo "  - Processed a GitHub webhook"
    echo "  - Created a PR on GitHub"
    echo "  - Passed validation checks"
else
    echo ""
    echo "❌ BLACK BOX TEST FAILED"
    echo "Check the output above for details"
fi