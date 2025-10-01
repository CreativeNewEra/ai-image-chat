#!/bin/bash
# Quick code quality checks before committing

echo "🔍 AI Image Chat - Code Quality Check"
echo "======================================"
echo ""

# Check Python syntax
echo "✓ Checking Python syntax..."
python -m py_compile app.py comfyui_api.py config.py 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ No syntax errors"
else
    echo "  ❌ Syntax errors found!"
    exit 1
fi
echo ""

# Check for common issues
echo "✓ Checking for common issues..."

# Check for print statements (should use logging)
print_count=$(grep -n "print(" app.py comfyui_api.py | grep -v "# DEBUG:" | wc -l)
echo "  ⚠️  Found $print_count print() statements (consider using logging)"

# Check for TODO/FIXME comments
todo_count=$(grep -rn "TODO\|FIXME" *.py | wc -l)
if [ $todo_count -gt 0 ]; then
    echo "  📝 Found $todo_count TODO/FIXME comments:"
    grep -rn "TODO\|FIXME" *.py | head -5
fi

echo ""

# Check file sizes
echo "✓ Code metrics..."
echo "  app.py: $(wc -l < app.py) lines"
echo "  comfyui_api.py: $(wc -l < comfyui_api.py) lines"
echo "  config.py: $(wc -l < config.py) lines"

app_lines=$(wc -l < app.py)
if [ $app_lines -gt 2000 ]; then
    echo "  ⚠️  app.py is getting large ($app_lines lines) - consider splitting"
fi

echo ""

# Check for required files
echo "✓ Checking required files..."
required_files=("README.md" "requirements.txt" "config.py" "CLAUDE.md" "TROUBLESHOOTING.md")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file missing!"
    fi
done

echo ""

# Check if outputs directory exists
if [ -d "outputs" ]; then
    output_count=$(ls -1 outputs/*.png 2>/dev/null | wc -l)
    echo "✓ outputs/ directory: $output_count images"
else
    echo "✓ outputs/ directory: not yet created (will be created on first generation)"
fi

echo ""
echo "======================================"
echo "✅ Code quality check complete!"
echo ""
echo "💡 Tips:"
echo "  - Run 'python test_new_features.py' to test core logic"
echo "  - Check TROUBLESHOOTING.md if you encounter issues"
echo "  - See BEST_PRACTICES.md for improvement suggestions"
echo ""
