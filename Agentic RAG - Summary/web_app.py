"""
Model White Paper Summary Application
Powered by Cohere Compass RAG & Command A
"""
import streamlit as st
import asyncio
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from config import config
from document_processor import DocumentProcessor
from cohere_compass import CohereCompassRAG

# Page configuration
st.set_page_config(
    page_title="Model White Paper Summary",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'white_paper_summary' not in st.session_state:
    st.session_state.white_paper_summary = None

class StreamlitApp:
    """Streamlit application wrapper"""
    
    def __init__(self):
        self.doc_processor = DocumentProcessor()
        try:
            self.compass_rag = CohereCompassRAG()
        except Exception as e:
            st.warning(f"Cohere Compass RAG not initialized: {e}")
            self.compass_rag = None
    
    def run(self):
        """Run the Streamlit application"""
        st.title("📄 Model White Paper Summary 🤖")
        st.markdown("*Powered by Cohere Compass RAG & Command A*")
        st.markdown("---")
        
        # Sidebar navigation
        page = st.sidebar.selectbox(
            "Navigation",
            ["Home", "White Paper Summary", "Settings"],
            key="navigation_selectbox"
        )
        
        if page == "Home":
            self.show_home_page()
        elif page == "White Paper Summary":
            self.show_white_paper_summary()
        elif page == "Settings":
            self.show_settings()
            
        # Add footer with copyright
        st.markdown("---")
        st.markdown(
            f"<div style='text-align: center; color: #666666; padding: 20px;'>"
            f"© {datetime.now().year} Model White Paper Summary. All rights reserved."
            "</div>", 
            unsafe_allow_html=True
        )
    
    def show_home_page(self):
        """Display home page"""
        st.header("📄 Model White Paper Summary System")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            **Transform complex model white papers into comprehensive, human-like summaries instantly.**
            
            ### ✨ **How It Works:**
            **📄 Upload** - Upload model white papers (~150 pages) in PDF, TXT, MD, or DOCX formats
            
            **🤖 AI Processing** - Cohere's Compass RAG reads and understands the entire document with advanced context handling
            
            **📋 Generate Summary** - Command A model generates a comprehensive, human-like summary without missing important details
            
            **🔑 Key Insights** - Automatically extract structured key information including:
            - Model name, type, and objectives
            - Methodology and technical approach
            - Data sources and requirements
            - Performance metrics
            - Risk factors and limitations
            - Regulatory considerations
            - Implementation requirements
            
            **💾 Export** - Download summaries in Markdown or JSON format for easy integration
            
            ### 🎯 **Key Features:**
            - **Comprehensive Analysis**: Detailed summaries covering all aspects of the model
            - **No Information Loss**: AI ensures all important details are captured
            - **Structured Output**: Organized sections with clear hierarchy
            - **Human-like Quality**: Natural language summaries that read professionally
            - **Fast Processing**: Handle large documents efficiently with smart chunking
            - **Multiple Formats**: Support for PDF, Word, Markdown, and Text files
            
            ### 🔧 **Technology:**
            - **Cohere Compass RAG**: Advanced retrieval-augmented generation
            - **Command A Model**: State-of-the-art language model with 256K token context
            - **Smart Chunking**: Intelligent document processing for optimal results
            """)
        
        with col2:
            st.success("""
            **🚀 Quick Start:**
            1. Go to **White Paper Summary**
            2. Upload **model white paper** (up to 150 pages)
            3. Enable **Detailed Analysis** and **Key Information**
            4. Click **Generate Summary**
            5. Review and **export** the comprehensive summary
            """)
            
            st.info("""
            **📌 Requirements:**
            - Cohere API key required
            - Get your key at: https://dashboard.cohere.com/api-keys
            - File sizes up to 150 pages supported
            """)
        
        # System Status
        st.subheader("🔧 System Status")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("AI Model", "Command A")
        
        with col2:
            api_status = "🟢 Active" if config.llm.cohere_api_key else "🟡 Not Configured"
            st.metric("Cohere Status", api_status)
        
        with col3:
            st.metric("Document Formats", "PDF, TXT, MD, DOCX")
        
        with col4:
            st.metric("Max Document Size", "150 Pages")
    
    def show_white_paper_summary(self):
        """Display White Paper Summary Interface using Cohere Compass RAG"""
        st.header("📄 Model White Paper Summary")
        
        st.info("""
        **Overview:**
        - Upload a model white paper (~150 pages)
        - Use Cohere's Compass RAG to read and understand the document
        - Generate a comprehensive summary using Cohere's Command A model
        - Get a human-like summary without missing any important details
        """)
        
        # Initialize session state for summary
        if 'white_paper_file_path' not in st.session_state:
            st.session_state.white_paper_file_path = None
        
        # File upload section
        st.subheader("📤 Upload Model White Paper")
        
        with st.form("white_paper_form"):
            white_paper = st.file_uploader(
                "Upload White Paper",
                type=['pdf', 'txt', 'md', 'docx'],
                help="Upload model white paper document (up to 150 pages supported)"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                include_detailed_analysis = st.checkbox(
                    "Include Detailed Analysis", 
                    value=True,
                    help="Generate a comprehensive analysis with all sections"
                )
            
            with col2:
                extract_key_info = st.checkbox(
                    "Extract Key Information",
                    value=True,
                    help="Extract structured key information from the document"
                )
            
            submitted = st.form_submit_button("🚀 Generate Summary")
            
            if submitted and white_paper:
                if self.compass_rag is None:
                    st.error("❌ Cohere Compass RAG is not initialized. Please check your COHERE_API_KEY in Settings.")
                    return
                
                with st.spinner("Processing white paper and generating comprehensive summary..."):
                    try:
                        # Save uploaded file temporarily
                        temp_path = Path(f"temp_{white_paper.name}")
                        with open(temp_path, "wb") as f:
                            f.write(white_paper.getvalue())
                        
                        st.session_state.white_paper_file_path = str(temp_path)
                        
                        # Process document with progress indicators
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        status_text.text("Step 1/3: Extracting content from document...")
                        progress_bar.progress(20)
                        
                        document_content = asyncio.run(self.compass_rag.process_white_paper(str(temp_path)))
                        
                        status_text.text("Step 2/3: Generating comprehensive summary with Cohere Command A...")
                        progress_bar.progress(50)
                        
                        summary_data = asyncio.run(self.compass_rag.generate_summary(
                            document_content, 
                            include_details=include_detailed_analysis
                        ))
                        
                        # Extract key information if requested
                        if extract_key_info:
                            status_text.text("Step 3/3: Extracting key information...")
                            progress_bar.progress(80)
                            
                            key_info = asyncio.run(self.compass_rag.extract_key_information(document_content))
                            summary_data["key_information"] = key_info
                        
                        progress_bar.progress(100)
                        status_text.text("Complete!")
                        
                        st.session_state.white_paper_summary = summary_data
                        
                        # Clean up temp file
                        temp_path.unlink()
                        
                        st.success("✅ White paper summary generated successfully!")
                        
                    except Exception as e:
                        st.error(f"❌ Error processing white paper: {e}")
                        import traceback
                        with st.expander("Error Details"):
                            st.code(traceback.format_exc())
        
        # Display summary if available
        if st.session_state.white_paper_summary:
            self._display_white_paper_summary(st.session_state.white_paper_summary)
    
    def _display_white_paper_summary(self, summary_data: dict):
        """Display the generated white paper summary"""
        st.subheader("📋 Generated Summary")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Document Length", f"{summary_data.get('document_length', 0):,} chars")
        
        with col2:
            st.metric("Chunks Processed", summary_data.get('chunks_processed', 0))
        
        with col3:
            st.metric("Model Used", summary_data.get('model_used', 'N/A'))
        
        with col4:
            summary_length = len(summary_data.get('summary', ''))
            st.metric("Summary Length", f"{summary_length:,} chars")
        
        # Display the summary
        st.markdown("### 📝 Comprehensive Summary")
        st.markdown(summary_data.get('summary', 'No summary available'))
        
        # Display key sections if available
        if 'key_sections' in summary_data and summary_data['key_sections']:
            st.markdown("### 📑 Key Sections")
            for i, section in enumerate(summary_data['key_sections'][:10]):  # Show first 10 sections
                with st.expander(f"{i+1}. {section.get('title', 'Section')}"):
                    st.markdown(section.get('content', ''))
        
        # Display extracted key information if available
        if 'key_information' in summary_data:
            st.markdown("### 🔑 Extracted Key Information")
            
            key_info = summary_data['key_information']
            
            # Check if it's a structured dict or raw response
            if isinstance(key_info, dict) and 'raw_response' not in key_info:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Model Details**")
                    if 'model_name' in key_info:
                        st.write(f"**Model Name:** {key_info['model_name']}")
                    if 'model_type' in key_info:
                        st.write(f"**Model Type:** {key_info['model_type']}")
                    if 'primary_objective' in key_info:
                        st.write(f"**Objective:** {key_info['primary_objective']}")
                    if 'methodology' in key_info:
                        st.write(f"**Methodology:** {key_info['methodology']}")
                
                with col2:
                    st.markdown("**Key Attributes**")
                    if 'key_assumptions' in key_info:
                        st.write("**Assumptions:**")
                        for assumption in key_info['key_assumptions'][:5]:
                            st.write(f"- {assumption}")
            
            with st.expander("View Full Key Information"):
                st.json(key_info)
        
        # Export options
        st.subheader("💾 Export Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Export as Markdown"):
                markdown_export = f"# Model White Paper Summary\n\n"
                markdown_export += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                markdown_export += f"## Summary\n\n{summary_data.get('summary', '')}\n\n"
                
                if 'key_sections' in summary_data:
                    markdown_export += f"## Key Sections\n\n"
                    for section in summary_data['key_sections']:
                        markdown_export += f"### {section.get('title', 'Section')}\n\n{section.get('content', '')}\n\n"
                
                st.download_button(
                    label="📥 Download Markdown",
                    data=markdown_export,
                    file_name=f"white_paper_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
        
        with col2:
            if st.button("📊 Export as JSON"):
                st.download_button(
                    label="📥 Download JSON",
                    data=json.dumps(summary_data, indent=2),
                    file_name=f"white_paper_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with col3:
            if st.button("🔄 Regenerate Summary"):
                st.session_state.white_paper_summary = None
                st.rerun()
    
    def show_settings(self):
        """Display settings page"""
        st.header("⚙️ Settings")
        
        st.subheader("🔧 System Configuration")
        
        # API Key Status
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🔑 API Key Status**")
            cohere_status = "✅ Set" if config.llm.cohere_api_key else "❌ Not Set"
            
            st.markdown(f"- **Cohere API** (Required): {cohere_status}")
            
            if config.llm.cohere_api_key:
                st.markdown(f"- Cohere Key Length: {len(config.llm.cohere_api_key)}")
        
        with col2:
            st.markdown("**📊 System Status**")
            if config.llm.cohere_api_key:
                st.success("🟢 Cohere Compass RAG Active")
            else:
                st.warning("🟡 No Cohere API Key Configured")
        
        # Configuration display
        with st.expander("📋 Configuration Details"):
            config_data = {
                "LLM Configuration": {
                    "Default Provider": config.llm.default_provider,
                    "Model Name": config.llm.model_name,
                    "Temperature": config.llm.temperature,
                    "Max Tokens": config.llm.max_tokens
                }
            }
            st.json(config_data)
        
        # Setup instructions
        st.subheader("🔧 Environment Setup")
        
        with st.expander("📝 Setup Instructions"):
            st.markdown("""
            ### Setting Up API Keys
            
            1. **Create a `.env` file** in your project root directory
            2. **Add your API key** to the `.env` file:
            
            ```env
            # Cohere API Key (Required)
            COHERE_API_KEY=your-cohere-api-key-here
            ```
            
            3. **Get Your Cohere API Key:**
               - Visit: https://dashboard.cohere.com/api-keys
               - Sign up or log in
               - Create a new API key
               - Copy and add to your `.env` file
            
            4. **Restart the application** after adding keys
            
            **📌 Note:** This application uses Cohere Compass RAG and Command A model exclusively
            """)
        
        st.info("""
        **💡 Pro Tips:**
        - Cohere API key is required for White Paper Summary
        - Get your key at: https://dashboard.cohere.com/api-keys
        - The system uses Cohere Command A for high-quality summaries
        - All generated summaries are comprehensive and human-like
        """)

def main():
    """Main function to run the Streamlit app"""
    app = StreamlitApp()
    app.run()

if __name__ == "__main__":
    main()
