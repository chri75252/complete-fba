#!/bin/bash
echo "🔧 Setting up FBA Tool Development Environment..."

# Install core requirements first
echo "Installing core requirements..."
pip install -r requirements.txt

# Additional development tools not in requirements.txt
echo "Installing additional development tools..."
pip install selenium selenium-wire undetected-chromedriver
pip install jupyter notebook ipython  # For data analysis
pip install scrapy requests-html httpx  # Enhanced scraping
pip install matplotlib seaborn plotly  # Data visualization
pip install xlswriter ruff  # Excel export and modern linting

# Optional database tools (for future upgrade)
echo "Installing optional database tools..."
pip install sqlalchemy alembic || echo "⚠️ Database tools optional - install manually if needed"

# Optional parallel testing
echo "Installing optional testing tools..."
pip install pytest-xdist || echo "⚠️ Parallel testing optional - install manually if needed"

echo "✅ FBA Development environment ready"
echo "📝 Next: Set OPENAI_API_KEY environment variable"