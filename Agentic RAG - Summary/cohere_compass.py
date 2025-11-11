"""
Cohere Compass RAG Integration for Model White Paper Processing
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
try:
    import cohere  # type: ignore
except ImportError:
    cohere = None  # type: ignore

from config import config
from document_processor import DocumentProcessor

logger = logging.getLogger(__name__)


class CohereCompassRAG:
    """Cohere Compass RAG for processing and understanding model white papers"""
    
    def __init__(self):
        if cohere is None:
            raise ImportError("cohere package is not installed. Please run: pip install cohere")
        
        if not config.llm.cohere_api_key:
            raise ValueError("COHERE_API_KEY not set in environment variables")
        
        self.client = cohere.Client(api_key=config.llm.cohere_api_key)
        self.model = config.llm.model_name
        self.doc_processor = DocumentProcessor()
        self.max_chunk_size = 10000  # Characters per chunk
        
    async def process_white_paper(self, file_path: str) -> str:
        """Process white paper document and extract full content"""
        try:
            logger.info(f"Processing white paper: {file_path}")
            
            # Extract content from document
            content = await self.doc_processor.process_document(file_path)
            
            if not content:
                raise ValueError(f"Could not extract content from {file_path}")
            
            logger.info(f"Extracted {len(content)} characters from white paper")
            return content
            
        except Exception as e:
            logger.error(f"Error processing white paper: {e}")
            raise
    
    def _chunk_document(self, content: str, chunk_size: Optional[int] = None) -> List[str]:
        """Split document into manageable chunks for processing"""
        if chunk_size is None:
            chunk_size = self.max_chunk_size
        
        chunks = []
        
        # Split by paragraphs first
        paragraphs = content.split('\n\n')
        
        current_chunk = ""
        for para in paragraphs:
            # If adding this paragraph doesn't exceed chunk size, add it
            if len(current_chunk) + len(para) < chunk_size:
                current_chunk += para + "\n\n"
            else:
                # Save current chunk and start new one
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        # Add remaining content
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    async def generate_summary(self, document_content: str, include_details: bool = True) -> Dict[str, Any]:
        """Generate comprehensive summary using Cohere Command A"""
        try:
            logger.info("Generating summary using Cohere Command A")
            
            # Chunk the document if it's very long
            chunks = self._chunk_document(document_content)
            logger.info(f"Document split into {len(chunks)} chunks")
            
            # Generate summary with Cohere Command A
            summary_prompt = self._create_summary_prompt(document_content, include_details)
            
            response = self.client.chat(
                model=self.model,
                message=summary_prompt,
                temperature=config.llm.temperature,
                max_tokens=config.llm.max_tokens
            )
            
            summary_text = response.text
            
            # Parse and structure the summary
            summary_data = {
                "summary": summary_text,
                "document_length": len(document_content),
                "chunks_processed": len(chunks),
                "model_used": self.model
            }
            
            # Extract key sections from summary if possible
            summary_data["key_sections"] = self._extract_key_sections(summary_text)
            
            logger.info("Summary generated successfully")
            return summary_data
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            raise
    
    def _create_summary_prompt(self, content: str, include_details: bool = True) -> str:
        """Create a comprehensive prompt for summary generation"""
        
        base_prompt = """You are an expert AI assistant specialized in analyzing and summarizing complex technical documents, particularly model white papers for financial and risk management systems.

TASK: Generate a comprehensive, human-like summary of the following model white paper. The summary should be thorough, well-structured, and capture ALL important details without missing any critical information.

DOCUMENT CONTENT:
"""
        
        # Include relevant portion of content (Command A can handle large context)
        # Take first 50000 characters for safety (Command A has 256K token context)
        truncated_content = content[:50000] if len(content) > 50000 else content
        
        prompt = base_prompt + "\n" + truncated_content + "\n\n"
        
        if include_details:
            prompt += """
INSTRUCTIONS FOR SUMMARY:
1. **Executive Overview** (2-3 paragraphs): Provide a high-level overview of the model, its purpose, and key objectives
2. **Model Methodology** (detailed section): Explain the technical approach, algorithms, methodologies, and underlying assumptions
3. **Data Requirements** (detailed section): Describe all data sources, data quality requirements, preprocessing steps, and data lineage
4. **Key Features and Components** (detailed section): List and explain all important features, components, and modules of the model
5. **Performance Metrics** (detailed section): Document all performance measures, benchmarks, and evaluation criteria
6. **Risk Considerations** (detailed section): Identify and analyze all risk factors, limitations, and mitigation strategies
7. **Regulatory Compliance** (detailed section): Note any regulatory requirements, compliance aspects, and governance considerations
8. **Implementation Details** (detailed section): Cover deployment architecture, integration points, and operational considerations
9. **Conclusions and Recommendations** (1-2 paragraphs): Summarize key takeaways and any recommendations or next steps
10. **Technical Specifications** (detailed section): Include any technical parameters, configurations, or specifications mentioned

WRITING STYLE:
- Write in a professional, clear, and comprehensive manner
- Use appropriate technical terminology while remaining accessible
- Ensure the summary is self-contained and can be understood without reading the original
- Include specific numbers, metrics, and details where mentioned in the document
- Organize information logically and hierarchically
- Do NOT omit any important details - completeness is critical

FORMAT: Provide the summary in well-structured sections with clear headings and subheadings using markdown formatting.
"""
        else:
            prompt += """
INSTRUCTIONS: Provide a concise but comprehensive summary covering the main points of the document.
"""
        
        return prompt
    
    def _extract_key_sections(self, summary_text: str) -> List[Dict[str, str]]:
        """Extract key sections from summary text"""
        sections = []
        
        # Try to identify markdown headers
        lines = summary_text.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            if line.startswith('#'):
                # New section found
                if current_section:
                    sections.append({
                        "title": current_section,
                        "content": '\n'.join(current_content).strip()
                    })
                current_section = line.lstrip('#').strip()
                current_content = []
            else:
                if line.strip():
                    current_content.append(line)
        
        # Add final section
        if current_section:
            sections.append({
                "title": current_section,
                "content": '\n'.join(current_content).strip()
            })
        
        return sections
    
    async def answer_questions(self, document_content: str, questions: List[str]) -> Dict[str, str]:
        """Answer questions about the document using RAG"""
        try:
            logger.info(f"Answering {len(questions)} questions about the document")
            
            answers = {}
            
            for question in questions:
                # Create a prompt that includes document context
                prompt = f"""Based on the following document content, please answer the question comprehensively and accurately.

DOCUMENT CONTENT:
{document_content[:30000]}

QUESTION: {question}

Provide a detailed, accurate answer based on the document. If the information is not available in the document, state that clearly.
"""
                
                response = self.client.chat(
                    model=self.model,
                    message=prompt,
                    temperature=0.2,  # Lower temperature for factual answers
                    max_tokens=2000
                )
                
                answers[question] = response.text
            
            logger.info("Questions answered successfully")
            return answers
            
        except Exception as e:
            logger.error(f"Error answering questions: {e}")
            raise
    
    async def extract_key_information(self, document_content: str) -> Dict[str, Any]:
        """Extract key information sections from the document"""
        try:
            logger.info("Extracting key information from document")
            
            extraction_prompt = """Based on the document content provided, extract the following key information in a structured JSON format:

{
    "model_name": "Name of the model",
    "model_type": "Type/category of the model",
    "primary_objective": "Main objective or purpose",
    "methodology": "Brief description of methodology",
    "key_assumptions": ["List of key assumptions"],
    "data_sources": ["List of data sources"],
    "performance_metrics": ["List of performance metrics"],
    "key_limitations": ["List of limitations"],
    "risk_factors": ["List of risk factors"],
    "regulatory_considerations": ["List of regulatory aspects"],
    "implementation_requirements": ["List of implementation requirements"]
}

DOCUMENT CONTENT:
""" + document_content[:30000] + "\n\nProvide the information in valid JSON format."
            
            response = self.client.chat(
                model=self.model,
                message=extraction_prompt,
                temperature=0.1,  # Very low temperature for structured extraction
                max_tokens=3000
            )
            
            # Try to parse JSON response
            import json
            try:
                extracted_info = json.loads(response.text)
            except json.JSONDecodeError:
                # If not valid JSON, return raw text
                extracted_info = {"raw_response": response.text}
            
            logger.info("Key information extracted successfully")
            return extracted_info
            
        except Exception as e:
            logger.error(f"Error extracting key information: {e}")
            raise