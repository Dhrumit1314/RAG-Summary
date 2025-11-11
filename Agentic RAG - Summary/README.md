# Model White Paper Summary

AI-powered model white paper summarization using **Cohere Compass RAG** and **Command A**.

## Features

- 📄 Upload model white papers (up to 150 pages) in PDF, TXT, MD, or DOCX formats
- 🤖 AI-powered processing using Cohere's Compass RAG for advanced context understanding
- 📋 Comprehensive summaries generated with Cohere Command A model
- 🔑 Automatic key information extraction
- 💾 Export summaries in Markdown or JSON formats
- 🌐 Web-based interface using Streamlit

## Technology Stack

- **Cohere Compass RAG**: Advanced retrieval-augmented generation for document understanding
- **Cohere Command A**: State-of-the-art language model with 256K token context
- **Streamlit**: Interactive web interface
- **Python**: Backend processing

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Cohere API Key

1. Visit [https://dashboard.cohere.com/api-keys](https://dashboard.cohere.com/api-keys)
2. Sign up or log in
3. Create a new API key
4. Copy the API key

### 3. Configure Environment

Create a `.env` file in the project root:

```env
COHERE_API_KEY=your-cohere-api-key-here
```

### 4. Run the Application

```bash
streamlit run web_app.py
```

The app will open at `http://localhost:8501`

## Usage

1. Navigate to **"White Paper Summary"** in the sidebar
2. Upload your model white paper document
3. Enable **"Detailed Analysis"** for comprehensive summaries
4. Enable **"Extract Key Information"** for structured data
5. Click **"Generate Summary"**
6. Review and export your summary

## Project Structure

```
MCP/
├── web_app.py              # Streamlit web application
├── cohere_compass.py       # Cohere RAG integration
├── document_processor.py   # Document processing utilities
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
├── PHASE1_SETUP.md         # Detailed setup guide
├── uploads/                # Upload directory (auto-created)
└── outputs/                # Output directory (auto-created)
```

## Requirements

- Python 3.8+
- Cohere API key
- Dependencies listed in `requirements.txt`

## Documentation

For detailed setup instructions, see [PHASE1_SETUP.md](PHASE1_SETUP.md)

## Support

For issues or questions:
- Check API key configuration in Settings
- Review error messages in the application
- Ensure all dependencies are installed correctly

---

**Powered by Cohere Compass RAG & Command A**

