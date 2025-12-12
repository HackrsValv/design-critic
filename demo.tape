# Design Critic Demo - Terminal GIF
# Run: vhs demo.tape

Output demo.gif

Set FontSize 16
Set Width 1000
Set Height 700
Set Theme "Catppuccin Mocha"
Set Padding 20
Set TypingSpeed 50ms
Set Shell "bash"
Set WindowBar Colorful

# Setup - hidden
Hide
Type "cd /Users/saint/Documents/ManualLibrary/repo.nosync/design-critic && clear"
Enter
Sleep 500ms
Show

# Header
Type "echo ''"
Enter
Type "echo '  Design Critic - AI-Powered Design Feedback'"
Enter
Type "echo '  Get instant critique from GPT-4o, Claude, or Gemini'"
Enter
Type "echo ''"
Enter
Sleep 1s

# Step 1: Health check
Type "echo 'Step 1: Check server health'"
Enter
Sleep 300ms
Type "curl -s localhost:8000/health | jq ."
Enter
Sleep 2s

# Step 2: Providers
Type "echo ''"
Enter
Type "echo 'Step 2: Available AI providers'"
Enter
Sleep 300ms
Type "curl -s localhost:8000/api/providers | jq ."
Enter
Sleep 3s

# Step 3: Show API usage example
Type "echo ''"
Enter
Type "echo 'Step 3: Critique a design via API'"
Enter
Sleep 300ms
Type "cat << 'EXAMPLE'"
Enter
Type "curl -X POST localhost:8000/api/critique"
Enter
Type "  -H Content-Type: application/json"
Enter
Type "  -d {"
Enter
Type "    html: <your html>,"
Enter
Type "    provider: openai,"
Enter
Type "    api_key: sk-your-key,"
Enter
Type "    design_type: email"
Enter
Type "  }"
Enter
Type "EXAMPLE"
Enter
Sleep 2s

# Step 4: Sample response
Type "echo ''"
Enter
Type "echo 'Step 4: Sample response structure'"
Enter
Sleep 300ms
Type "cat << 'JSON' | jq ."
Enter
Type '{"overall_score":7,"summary":"Clean design with room for improvement","strengths":["Good typography","Nice colors"],"improvements":["Increase CTA size"]}'
Enter
Type "JSON"
Enter
Sleep 3s

# Features
Type "echo ''"
Enter
Type "echo 'Features:'"
Enter
Type "echo '  - Upload images, paste HTML, or provide URLs'"
Enter
Type "echo '  - BYOK: API keys stay in your browser'"
Enter
Type "echo '  - Detailed scores for hierarchy, typography, colors'"
Enter
Type "echo '  - Actionable suggestions for each area'"
Enter
Sleep 2s

# Web UI
Type "echo ''"
Enter
Type "echo 'Web UI: http://localhost:8000'"
Enter
Sleep 500ms

# End
Type "echo ''"
Enter
Type "echo 'Get started:'"
Enter
Type "echo '  uv run python -m design_critic.api'"
Enter
Sleep 3s
