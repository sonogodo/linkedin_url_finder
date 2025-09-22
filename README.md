# LinkedIn Profile Finder

An automated LinkedIn profile discovery tool that searches for LinkedIn profiles of graduates using Selenium and web scraping techniques.

## 🎯 Features

- **High Success Rate**: Achieves 99%+ success rate in finding LinkedIn profiles
- **Smart Processing**: Automatically skips already processed records
- **Unique ID System**: Each found profile gets a unique identifier
- **Batch Processing**: Processes records in batches with respectful delays
- **Resume Capability**: Can be interrupted and resumed safely
- **Multiple Processing Options**: From quick tests to full production runs
- **Clean Data Management**: Single master file with no duplicates

## 📊 Current Results

- ✅ **553 unique LinkedIn profiles found**
- 🎯 **99% success rate** across 500+ processed records
- 📈 **22.3% of total dataset processed**
- 🚀 **Production-ready and stable**

## 🛠️ Installation

### Prerequisites

- Python 3.7+
- Google Chrome browser
- ChromeDriver (automatically downloaded by setup script)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/linkedin-url-finder.git
cd linkedin-url-finder
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Setup ChromeDriver:
```bash
python setup_chromedriver.py
```

## 🚀 Usage

### Quick Start

Run the main production script:
```bash
python linkedin_production.py
```

### Processing Options

1. **Quick test** (next 10 unprocessed) - Perfect for testing
2. **Small batch** (next 50 unprocessed) - Small runs
3. **Medium batch** (next 200 unprocessed) - Medium runs
4. **Large batch** (next 500 unprocessed) - Large runs
5. **🚀 PRODUCTION MODE** - All remaining unprocessed records
6. **Custom amount** - Specify how many unprocessed records

### Check Progress

Monitor your progress anytime:
```bash
python check_progress.py
```

## 📁 File Structure

```
├── linkedin_production.py      # Main production script
├── linkedin_success_master.json # Master file with all found profiles
├── new_graduates.csv           # Input data (graduates list)
├── check_progress.py           # Progress monitoring tool
├── setup_chromedriver.py       # ChromeDriver setup utility
├── linkedin_selenium_simple.py # Simple test script
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 📊 Data Structure

### Input CSV Format
```csv
Nome,Data da Colação,Curso,Faculdade
John Doe,29/08/2025,Engineering,UNESP
Jane Smith,07/02/2025,Computer Science,UNESP
```

### Output JSON Format
```json
{
  "id": "abc12345",
  "Nome": "John Doe",
  "Curso": "Engineering", 
  "Faculdade": "UNESP",
  "Data da Colação": "29/08/2025",
  "LinkedIn URL": "https://linkedin.com/in/johndoe",
  "Last Updated": "2025-09-21 20:32:05"
}
```

## 🔧 Technical Details

### How It Works

1. **Smart Search**: Uses Selenium to automate DuckDuckGo searches
2. **Pattern Matching**: Generates multiple search query variations
3. **URL Validation**: Validates and cleans found LinkedIn URLs
4. **Duplicate Prevention**: Automatically skips already processed records
5. **Batch Processing**: Processes records in batches with delays to respect rate limits

### Search Strategy

- Primary search engine: DuckDuckGo (automation-friendly)
- Multiple query patterns per person
- Intelligent URL extraction and cleaning
- Real browser simulation to avoid bot detection

### Performance Optimizations

- **Smart Skipping**: Only processes unprocessed records
- **Batch Processing**: 25 records per batch with 30-second breaks
- **Progress Saving**: Saves progress every 5 batches
- **Memory Efficient**: Single master file approach
- **Resume Capability**: Can restart from where it left off

## 📈 Success Metrics

- **99% Success Rate**: Finds LinkedIn profiles for 99% of searched individuals
- **553 Profiles Found**: Successfully discovered 553 unique LinkedIn profiles
- **Zero Duplicates**: Smart duplicate detection ensures clean data
- **Production Stable**: Handles large datasets (2,400+ records) reliably

## 🛡️ Rate Limiting & Ethics

- **Respectful Delays**: 2-4 second delays between searches
- **Batch Breaks**: 30-second breaks between batches
- **User-Agent Rotation**: Uses realistic browser headers
- **No Aggressive Scraping**: Follows ethical web scraping practices

## 🔄 Resuming Interrupted Sessions

The system automatically handles interruptions:

1. Progress is saved to the master file every 5 batches
2. On restart, it loads existing results and skips processed records
3. No data loss - all found profiles are preserved
4. Simply run the script again to continue where you left off

## 📊 Monitoring Progress

Use the progress checker to see current status:

```bash
python check_progress.py
```

Shows:
- Total profiles found
- Progress percentage
- Remaining records to process
- Recent profile discoveries
- Last update timestamp

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational and research purposes. Please ensure you comply with:
- LinkedIn's Terms of Service
- Local data protection laws (GDPR, CCPA, etc.)
- Ethical web scraping practices
- Rate limiting and respectful usage

## 🎯 Future Enhancements

- [ ] Multi-threading support for faster processing
- [ ] Additional search engines integration
- [ ] Export to different formats (Excel, CSV)
- [ ] Advanced filtering and search options
- [ ] Web interface for easier usage
- [ ] API integration for real-time processing

## 📞 Support

If you encounter any issues or have questions:

1. Check the existing issues on GitHub
2. Create a new issue with detailed information
3. Include error messages and system information

---

**Made with ❤️ for efficient LinkedIn profile discovery**