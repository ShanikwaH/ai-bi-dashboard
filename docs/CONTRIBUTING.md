# Contributing to AI-Powered BI Dashboard

First off, thank you for considering contributing to the AI-Powered Business Intelligence Dashboard! It's people like you that make this tool better for everyone.

## 🌟 Ways to Contribute

### 1. 🐛 Report Bugs
Found a bug? Help us fix it by creating a detailed issue.

### 2. 💡 Suggest Features
Have an idea for improvement? We'd love to hear it!

### 3. 📝 Improve Documentation
Documentation can always be better. Help others understand the project.

### 4. 🔧 Submit Code
Ready to dive into the code? We welcome pull requests!

### 5. 🧪 Test Features
Help test new features and provide feedback.

### 6. ❓ Answer Questions
Help other users in Discussions and Issues.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- Git installed
- GitHub account
- Basic understanding of Python and Streamlit
- Gemini API key (for testing AI features)

### Development Setup

**1. Fork the repository**
```bash
# Click "Fork" button on GitHub
```

**2. Clone your fork**
```bash
git clone https://github.com/YOUR_USERNAME/ai-bi-dashboard.git
cd ai-bi-dashboard
```

**3. Add upstream remote**
```bash
git remote add upstream https://github.com/ORIGINAL_OWNER/ai-bi-dashboard.git
```

**4. Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

**5. Install dependencies**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development tools
```

**6. Set up environment variables**
```bash
cp .env.example .env
# Add your GEMINI_API_KEY to .env
```

**7. Run the app**
```bash
streamlit run app.py
```

---

## 📋 Development Workflow

### 1. Create a Branch

**Always create a new branch for your work:**

```bash
git checkout -b feature/amazing-feature
```

**Branch naming conventions:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Adding tests

**Examples:**
```bash
git checkout -b feature/add-arima-forecasting
git checkout -b fix/forecast-interpretation-error
git checkout -b docs/update-installation-guide
```

### 2. Make Your Changes

**Follow our coding standards:**

**Python Style Guide (PEP 8):**
```python
# ✅ Good
def calculate_forecast(data: pd.Series, periods: int = 30) -> list:
    """
    Generate forecast for given time series data.
    
    Args:
        data: Time series data as Pandas Series
        periods: Number of periods to forecast
        
    Returns:
        List of forecasted values
    """
    forecast = []
    # Implementation here
    return forecast

# ❌ Bad
def calc(d,p=30):
    f=[]
    # Implementation
    return f
```

**Code Quality Checklist:**
- [ ] Code follows PEP 8 style guide
- [ ] Functions have docstrings
- [ ] Complex logic has comments
- [ ] Variable names are descriptive
- [ ] No hardcoded values (use constants)
- [ ] Error handling included
- [ ] Type hints where appropriate

### 3. Test Your Changes

**Run tests before committing:**

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_forecasting.py

# Run with coverage
pytest --cov=app tests/
```

**Manual testing checklist:**
- [ ] App starts without errors
- [ ] New feature works as expected
- [ ] Existing features still work
- [ ] AI integration functions properly
- [ ] No console errors
- [ ] Works on different datasets

### 4. Commit Your Changes

**Write clear, descriptive commit messages:**

```bash
# ✅ Good commit messages
git commit -m "Add ARIMA forecasting algorithm with parameter optimization"
git commit -m "Fix: Resolve forecast interpretation error for negative trends"
git commit -m "Docs: Update installation guide with troubleshooting section"

# ❌ Bad commit messages
git commit -m "update"
git commit -m "fix bug"
git commit -m "changes"
```

**Commit message format:**
```
<type>: <subject>

<body (optional)>

<footer (optional)>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Example:**
```
feat: Add Prophet forecasting algorithm

Implemented Facebook Prophet for time series forecasting with:
- Automatic seasonality detection
- Holiday effects support
- Trend changepoint detection
- Customizable uncertainty intervals

Closes #42
```

### 5. Push to Your Fork

```bash
git push origin feature/amazing-feature
```

### 6. Create Pull Request

**Go to GitHub and create a pull request:**

**PR Title Examples:**
- ✅ `Add ARIMA forecasting with automatic parameter selection`
- ✅ `Fix forecast interpretation for datasets with missing values`
- ✅ `Update documentation with advanced forecasting examples`

**PR Description Template:**
```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
Describe the tests you ran to verify your changes.

## Screenshots (if applicable)
Add screenshots showing the new feature or fix.

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes

## Related Issues
Closes #<issue_number>
```

---

## 🎨 Code Style Guide

### Python

**Follow PEP 8 with these specifics:**

**Imports:**
```python
# Standard library imports
import os
import sys
from datetime import datetime

# Third-party imports
import streamlit as st
import pandas as pd
import numpy as np

# Local imports
from utils import helpers
```

**Function Definitions:**
```python
def process_data(
    df: pd.DataFrame,
    column: str,
    method: str = "mean"
) -> pd.Series:
    """
    Process data using specified method.
    
    Args:
        df: Input dataframe
        column: Column name to process
        method: Processing method ('mean', 'median', 'mode')
        
    Returns:
        Processed data as Series
        
    Raises:
        ValueError: If column not found
    """
    if column not in df.columns:
        raise ValueError(f"Column {column} not found")
    
    # Implementation
    return processed_data
```

**Error Handling:**
```python
# ✅ Good
try:
    result = process_data(df)
except ValueError as e:
    st.error(f"Error processing data: {str(e)}")
    return None

# ❌ Bad
try:
    result = process_data(df)
except:
    pass
```

**Constants:**
```python
# ✅ Good - At top of file
DEFAULT_FORECAST_PERIODS = 30
MAX_UPLOAD_SIZE_MB = 200
SUPPORTED_MODELS = ['gemini-1.5-flash', 'gemini-1.5-pro']

# ❌ Bad - Hardcoded in functions
def forecast():
    periods = 30  # Magic number
```

### Streamlit

**Session State:**
```python
# ✅ Good - Initialize at start
if 'df' not in st.session_state:
    st.session_state.df = None

# Use throughout app
df = st.session_state.df

# ❌ Bad - Direct use without check
df = st.session_state.df  # May cause KeyError
```

**Layout:**
```python
# ✅ Good - Clear structure
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Revenue", "$1.2M")

with col2:
    st.metric("Growth", "15%")

# ❌ Bad - Unclear structure
st.columns(3)[0].metric("Revenue", "$1.2M")
```

---

## 🧪 Testing Guidelines

### Writing Tests

**Create test files in `tests/` directory:**

```python
# tests/test_forecasting.py
import pytest
import pandas as pd
import numpy as np
from app import moving_average_forecast, exponential_smoothing_forecast

def test_moving_average_forecast():
    """Test moving average forecasting function."""
    # Arrange
    data = pd.Series([100, 110, 105, 115, 120])
    
    # Act
    forecast = moving_average_forecast(data, window=3, periods=5)
    
    # Assert
    assert len(forecast) == 5
    assert all(isinstance(x, (int, float)) for x in forecast)
    assert forecast[0] > 0

def test_exponential_smoothing_forecast():
    """Test exponential smoothing forecasting."""
    data = pd.Series([100, 110, 105, 115, 120])
    forecast = exponential_smoothing_forecast(data, alpha=0.3, periods=5)
    
    assert len(forecast) == 5
    assert all(isinstance(x, (int, float)) for x in forecast)

def test_forecast_with_negative_values():
    """Test forecasting with negative values."""
    data = pd.Series([-10, -5, 0, 5, 10])
    forecast = moving_average_forecast(data, window=3, periods=3)
    
    assert len(forecast) == 3
    # Forecast should handle negative values
```

**Run tests:**
```bash
# All tests
pytest

# Specific file
pytest tests/test_forecasting.py

# With coverage
pytest --cov=app tests/

# Verbose output
pytest -v
```

---

## 📝 Documentation Standards

### Code Documentation

**Module Docstrings:**
```python
"""
Forecasting Module

This module provides time series forecasting capabilities including:
- Moving Average forecasting
- Exponential Smoothing
- ARIMA (planned)

Usage:
    from forecasting import MovingAverageForecast
    
    forecast = MovingAverageForecast(window=7)
    predictions = forecast.fit_predict(data, periods=30)
"""
```

**Function Docstrings:**
```python
def calculate_kpis(df: pd.DataFrame, date_col: str, value_col: str) -> dict:
    """
    Calculate key performance indicators for time series data.
    
    This function computes various metrics including total, mean, median,
    standard deviation, and growth rate for the specified value column.
    
    Args:
        df: DataFrame containing the time series data
        date_col: Name of the date/time column
        value_col: Name of the value column to analyze
        
    Returns:
        Dictionary containing:
            - total: Sum of all values
            - mean: Average value
            - median: Median value
            - std: Standard deviation
            - growth_rate: Percentage growth (recent vs previous)
            
    Raises:
        ValueError: If specified columns don't exist
        TypeError: If value_col is not numeric
        
    Examples:
        >>> df = pd.DataFrame({
        ...     'Date': pd.date_range('2024-01-01', periods=100),
        ...     'Revenue': np.random.normal(1000, 100, 100)
        ... })
        >>> kpis = calculate_kpis(df, 'Date', 'Revenue')
        >>> print(kpis['growth_rate'])
        5.2
    """
```

### User Documentation

**Update relevant docs when you:**
- Add new features → Update README.md and GETTING_STARTED.md
- Change API → Update AI_TUTORIAL.md
- Modify forecasting → Update FORECASTING.md
- Fix bugs → Update CHANGELOG.md

---

## 🏗️ Project Structure

```
ai-bi-dashboard/
│
├── app.py                      # Main application
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
│
├── tests/                      # Test files
│   ├── __init__.py
│   ├── test_forecasting.py
│   ├── test_ai_integration.py
│   └── test_data_processing.py
│
├── utils/                      # Utility modules (future)
│   ├── __init__.py
│   ├── forecasting.py
│   ├── ai_helpers.py
│   └── data_processing.py
│
├── docs/                       # Documentation
│   ├── GETTING_STARTED.md
│   ├── AI_TUTORIAL.md
│   ├── FORECASTING.md
│   └── API.md
│
├── .streamlit/
│   └── config.toml
│
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
│
└── data/                       # Sample data (gitignored)
```

---

## 🐛 Bug Reports

### Before Submitting

1. **Check existing issues** - Someone may have reported it already
2. **Update to latest version** - Bug might be fixed
3. **Test in clean environment** - Rule out local issues

### Creating a Bug Report

**Use the Bug Report template and include:**

1. **Clear title**: "Forecast generation fails with NaN values"
2. **Description**: What happened vs what should happen
3. **Steps to reproduce**:
   ```
   1. Upload dataset with missing values
   2. Navigate to Forecasting
   3. Click Generate Forecast
   4. Error appears
   ```
4. **Expected behavior**: "Should handle NaN values gracefully"
5. **Actual behavior**: "App crashes with KeyError"
6. **Screenshots**: If applicable
7. **Environment**:
   ```
   - OS: macOS 14.0
   - Python: 3.11.5
   - Streamlit: 1.39.0
   - Browser: Chrome 120
   ```
8. **Additional context**: Error logs, data samples, etc.

---

## 💡 Feature Requests

### Before Requesting

1. **Check roadmap** - Feature might be planned
2. **Search issues** - Feature might be requested
3. **Consider alternatives** - Existing features might work

### Creating a Feature Request

**Include:**

1. **Clear title**: "Add ARIMA forecasting algorithm"
2. **Problem statement**: "Current forecasting methods don't handle seasonality well"
3. **Proposed solution**: "Implement ARIMA with automatic parameter selection"
4. **Alternatives considered**: "Prophet, SARIMA, etc."
5. **Additional context**: Use cases, examples, mockups
6. **Willingness to contribute**: "I can implement this with guidance"

---

## 🔍 Code Review Process

### What We Look For

**✅ We will approve if:**
- Code follows style guide
- Tests pass
- Documentation updated
- No breaking changes (or well documented)
- Performance impact considered
- Security implications addressed

**❌ We will request changes if:**
- Code style violations
- Missing tests
- Undocumented changes
- Breaking changes without migration guide
- Security vulnerabilities
- Performance regressions

### Review Timeline

- **Simple fixes**: 1-2 days
- **New features**: 3-7 days
- **Major changes**: 1-2 weeks

We'll do our best to review quickly, but please be patient!

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## 🙏 Recognition

### Contributors

All contributors will be:
- Listed in README.md
- Mentioned in release notes
- Added to CONTRIBUTORS.md (if significant contribution)

### Hall of Fame

Exceptional contributors may be:
- Made collaborators
- Given special recognition
- Invited to help with roadmap

---

## ❓ Questions?

- 💬 **Discussions**: Ask general questions
- 📧 **Email**: nikki.19972010@hotmail.com
- 🐛 **Issues**: Technical questions about bugs

---

## 🚀 Areas We Need Help

### High Priority

- [ ] **Advanced Forecasting**: ARIMA, Prophet, LSTM
- [ ] **Real-time Data**: WebSocket integration
- [ ] **Testing**: Increase coverage to 80%+
- [ ] **Documentation**: Video tutorials
- [ ] **Performance**: Optimize for large datasets

### Medium Priority

- [ ] **UI/UX**: Mobile responsiveness
- [ ] **Internationalization**: Multiple languages
- [ ] **Database Integration**: PostgreSQL, MongoDB
- [ ] **Authentication**: User management
- [ ] **API**: REST endpoints

### Low Priority

- [ ] **Themes**: Dark mode, custom themes
- [ ] **Export**: PDF reports
- [ ] **Plugins**: Extension system
- [ ] **Notifications**: Email/SMS alerts

---

## 📚 Learning Resources

### New to Contributing?

- [First Contributions](https://github.com/firstcontributions/first-contributions)
- [How to Contribute to Open Source](https://opensource.guide/how-to-contribute/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)

### Learning the Tech Stack

- **Python**: [Official Tutorial](https://docs.python.org/3/tutorial/)
- **Streamlit**: [Documentation](https://docs.streamlit.io)
- **Pandas**: [10 Minutes to Pandas](https://pandas.pydata.org/docs/user_guide/10min.html)
- **Plotly**: [Getting Started](https://plotly.com/python/getting-started/)
- **Gemini AI**: [Quickstart](https://ai.google.dev/tutorials/python_quickstart)

---

## 🎯 Contributor Expectations

### What You Can Expect From Us

- ✅ Timely responses to issues and PRs
- ✅ Constructive feedback on contributions
- ✅ Credit for your work
- ✅ Welcoming and inclusive environment
- ✅ Help with getting started

### What We Expect From You

- ✅ Follow code of conduct
- ✅ Respect reviewer feedback
- ✅ Test your changes
- ✅ Document your code
- ✅ Be patient with review process
- ✅ Help others when you can

---

## 🤝 Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](docs/CODE_OF_CONDUCT.md).

**In short:**
- Be respectful and inclusive
- Accept constructive criticism gracefully  
- Focus on what's best for the community
- Show empathy towards others

---

## 🎉 Thank You!

Every contribution, no matter how small, makes this project better. Whether it's:
- Fixing a typo
- Reporting a bug
- Suggesting a feature
- Writing code
- Helping others

**You're making a difference. Thank you!** 🙌

---

**Happy Contributing!** 🚀

*Last updated: October 2025*
