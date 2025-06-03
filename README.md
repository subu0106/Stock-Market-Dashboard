# 📊 Stock Market Dashboard
A real-time stock market dashboard built with H2O Wave, featuring fast chart switching and efficient data caching.

## Screenshots & Demo

### Demo Video
<video width="800" controls>
  <source src="https://github.com/subu0106/Stock-Market-Dashboard/raw/main/assets/demo.mp4" type="video/mp4">
  <a href="https://github.com/subu0106/Stock-Market-Dashboard/blob/main/assets/demo.mp4">Watch Demo Video</a>
</video>


### Application Screenshots

#### Dark Theme

<div align="center">
  <img src="https://raw.githubusercontent.com/subu0106/Stock-Market-Dashboard/main/assets/DT-1.png" alt="Dark Theme View 1" width="45%">
  <img src="https://raw.githubusercontent.com/subu0106/Stock-Market-Dashboard/main/assets/DT-2.png" alt="Dark Theme View 2" width="45%">
</div>

####  Light Theme

<div align="center">
  <img src="https://raw.githubusercontent.com/subu0106/Stock-Market-Dashboard/main/assets/LT-1.png" alt="Light Theme View 1" width="45%">
  <img src="https://raw.githubusercontent.com/subu0106/Stock-Market-Dashboard/main/assets/LT-2.png" alt="Light Theme View 2" width="45%">
</div>

## Features

### Stock Market

- **Real-time Stock Data**: Live stock prices and market information via Yahoo Finance
- **Interactive Charts**: Multiple time periods (5D, 1M, 6M, 1Y, 5Y, Max)
- **Stock Search**: Fast ticker symbol search with suggestions
- **Market Metrics**: Key financial indicators and statistics

## Technical Stack

- **Backend**: Python 3.12+
- **Web Framework**: H2O Wave
- **Data Source**: Yahoo Finance API (yfinance)
- **UI Components**: H2O Wave UI framework
- **Caching**: In-memory caching with timestamp validation

## Installation

### Prerequisites
- Python 3.12 or higher
- pip package manager

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/subu0106/Stock-Market-Dashboard.git
   cd Stock-Market-Dashboard
   ```

2. **Create virtual environment**
   ```bash
   python -m venv wave-env
   source wave-env/bin/activate  # On macOS/Linux
   # or
   wave-env\Scripts\activate     # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   wave run app.py
   ```

5. **Access the dashboard**
   Open your browser and navigate to `http://localhost:10101`

## Project Structure

```
Stock-Market-Prediction/
├── app.py                    # Application entry point
├── requirements.txt          # Python dependencies
├── README.md                # Project documentation
├── assets/                   # Images and project resources
│   └── dashboard-screenshot.png
├── test/                     # Simple tests
│   ├── __init__.py
│   └── test.py              # Basic functionality tests
├── src/
│   ├── main.py              # Main application logic
│   ├── config/
│   │   ├── constants.py     # Configuration constants
│   │   └── __init__.py
│   ├── data/
│   │   ├── stock_service.py # Stock data service with caching
│   │   └── __init__.py
│   ├── ui/
│   │   ├── components.py    # Reusable UI components
│   │   ├── theme.py         # Theme management
│   │   └── __init__.py
│   ├── utils/
│   │   ├── helpers.py       # Utility functions
│   │   └── __init__.py
│   └── __init__.py
└── wave-env/                # Virtual environment
```

## Usage

1. **Search for a stock**: Type ticker symbol (e.g., "AAPL") in the search box
2. **Switch time periods**: Click period buttons (5D, 1M, 6M, etc.) for instant switching
3. **Toggle theme**: Click the theme button  in the header

## Testing

The project includes comprehensive test coverage to verify functionality:

### Run Tests

```bash
# Comprehensive test suite (full coverage)
python test/test.py
```

### Test Coverage

The tests verify:

- **Module Imports**: All modules can be imported successfully
- **Configuration**: Constants, themes, and app settings  
- **Stock Service**: Data fetching, caching, and chart operations
- **Helper Functions**: Validation, formatting, and search utilities
- **UI Components**: Header, search, tables, and chart creation

Both test suites use the project's proper package structure and run independently of the H2O Wave server.

## Acknowledgments

- **H2O Wave**: For the powerful web application framework
- **Yahoo Finance**: For providing free stock market data
- **Python Community**: For excellent libraries and tools

---
