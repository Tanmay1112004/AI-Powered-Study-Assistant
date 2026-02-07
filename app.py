import streamlit as st
import google.generativeai as genai
import os
import tempfile
import PyPDF2
import docx
import chromadb
import hashlib
from typing import List, Dict
import warnings
warnings.filterwarnings('ignore')

# Custom CSS for better UI
CUSTOM_CSS = """
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #4B5563;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 5px;
        font-weight: bold;
        width: 100%;
    }
    .upload-section {
        background-color: #F3F4F6;
        padding: 2rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 2px dashed #667eea;
    }
    .sidebar-content {
        background-color: #F8FAFC;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #D1FAE5;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #10B981;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #E0F2FE;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #0EA5E9;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #FEF3C7;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #F59E0B;
        margin: 1rem 0;
    }
    .chat-message-user {
        background-color: #E0F2FE;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .chat-message-assistant {
        background-color: #D1FAE5;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
</style>
"""

class StudyAssistant:
    def __init__(self, api_key: str):
        """Initialize the Study Assistant with Gemini API"""
        try:
            genai.configure(api_key=api_key)
            self.api_key = api_key
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            self.documents = []
            self.document_texts = []
            st.session_state.api_key_valid = True
        except Exception as e:
            st.error(f"Failed to initialize Gemini API: {str(e)}")
            st.session_state.api_key_valid = False
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            st.error(f"Failed to extract text from PDF: {str(e)}")
            return ""
        return text
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            st.error(f"Failed to extract text from DOCX: {str(e)}")
            return ""
    
    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            st.error(f"Failed to read TXT file: {str(e)}")
            return ""
    
    def process_uploaded_file(self, uploaded_file) -> str:
        """Process uploaded file and extract text"""
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        try:
            if file_extension == 'pdf':
                return self.extract_text_from_pdf(tmp_path)
            elif file_extension == 'docx':
                return self.extract_text_from_docx(tmp_path)
            elif file_extension in ['txt', 'md']:
                return self.extract_text_from_txt(tmp_path)
            else:
                st.error(f"Unsupported file type: {file_extension}")
                return ""
        finally:
            try:
                os.unlink(tmp_path)
            except:
                pass
    
    def split_text_into_chunks(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = min(start + chunk_size, text_length)
            
            # Try to end at a sentence boundary
            if end < text_length:
                # Look for sentence endings
                for punct in ['. ', '! ', '? ', '\n\n', '\n']:
                    punct_pos = text.rfind(punct, start, end)
                    if punct_pos != -1 and punct_pos > start + chunk_size // 2:
                        end = punct_pos + len(punct)
                        break
            
            chunk = text[start:end]
            if chunk.strip():
                chunks.append(chunk)
            
            start = end - overlap  # Overlap chunks
        
        return chunks
    
    def summarize_document(self, text: str) -> str:
        """Summarize the document"""
        if not text or len(text.strip()) < 50:
            return "Document content is too short to summarize."
            
        try:
            prompt = f"""You are an expert study assistant. Please provide a comprehensive yet concise summary of the following study material. 
            Focus on key concepts, important formulas, definitions, and main topics. Structure the summary with clear headings.

            Document content:
            {text[:5000]}  # Limiting context for efficiency

            Provide a structured summary with these sections:
            ## 📌 Main Topics Covered
            ## 🎯 Key Concepts
            ## 📐 Important Formulas/Theorems (if any)
            ## 💡 Study Recommendations
            ## 🚀 Quick Revision Points
            """
            
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def generate_questions(self, text: str, num_questions: int = 5, question_type: str = "Mixed") -> List[Dict]:
        """Generate exam questions from document"""
        if not text or len(text.strip()) < 100:
            return [{"error": "Document content is too short to generate questions."}]
            
        try:
            type_instruction = ""
            if question_type == "Multiple Choice":
                type_instruction = "Focus on multiple choice questions with 4 options."
            elif question_type == "Short Answer":
                type_instruction = "Focus on short answer questions (2-3 sentences)."
            elif question_type == "Problem Solving":
                type_instruction = "Focus on problem-solving questions with step-by-step solutions."
            
            prompt = f"""Generate {num_questions} {question_type.lower()} exam-style questions based on the following study material. 
            {type_instruction}
            
            Document content:
            {text[:4000]}
            
            Format each question as:
            ### Question [number]: [question text]
            **Type:** [multiple choice/short answer/problem solving]
            **Difficulty:** [Easy/Medium/Hard]
            **Topic:** [Main topic]
            
            For multiple choice questions, include:
            A. [Option A]
            B. [Option B]
            C. [Option C]
            D. [Option D]
            
            Provide answer explanation at the end of each question.
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse response into structured format
            questions = []
            sections = response.text.split('### Question')
            
            for section in sections[1:num_questions+1]:  # Skip first empty section
                lines = section.strip().split('\n')
                if not lines:
                    continue
                    
                question_data = {
                    'question': lines[0].strip(),
                    'type': '',
                    'difficulty': '',
                    'topic': '',
                    'options': [],
                    'answer': ''
                }
                
                for line in lines[1:]:
                    line = line.strip()
                    if line.startswith('**Type:**'):
                        question_data['type'] = line.replace('**Type:**', '').strip()
                    elif line.startswith('**Difficulty:**'):
                        question_data['difficulty'] = line.replace('**Difficulty:**', '').strip()
                    elif line.startswith('**Topic:**'):
                        question_data['topic'] = line.replace('**Topic:**', '').strip()
                    elif line.startswith(('A.', 'B.', 'C.', 'D.')):
                        question_data['options'].append(line.strip())
                    elif line.lower().startswith('answer'):
                        question_data['answer'] = line.strip()
                
                questions.append(question_data)
            
            return questions[:num_questions]
        except Exception as e:
            return [{"error": f"Error generating questions: {str(e)}"}]
    
    def explain_topic(self, topic: str) -> str:
        """Explain a topic in simple language"""
        if not topic.strip():
            return "Please enter a topic to explain."
            
        try:
            # Search in uploaded documents first
            context = ""
            for doc_text in self.document_texts:
                if topic.lower() in doc_text.lower():
                    # Get relevant portion
                    idx = doc_text.lower().find(topic.lower())
                    context = doc_text[max(0, idx-500):min(len(doc_text), idx+500)]
                    break
            
            prompt = f"""Explain the following topic in simple, easy-to-understand language as if teaching a beginner.
            Use analogies, real-world examples, and simple diagrams in text form where helpful.
            Break down complex concepts into step-by-step explanations.
            
            Topic to explain: {topic}
            
            Context from study materials (if available):
            {context}
            
            Structure your explanation as:
            ## 📖 What is {topic}? (Simple Definition)
            ## 🔍 Key Points Explained Simply
            ## 🌟 Real-world Example/Analogy
            ## ⚠️ Common Misconceptions to Avoid
            ## 💎 Quick Summary (3-5 bullet points)
            """
            
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error explaining topic: {str(e)}"
    
    def search_in_documents(self, query: str) -> str:
        """Search for relevant information in uploaded documents"""
        if not self.document_texts:
            return "No documents uploaded yet."
            
        try:
            # Simple keyword-based search (for demo)
            relevant_texts = []
            for doc_text in self.document_texts:
                # Check if query keywords are in the document
                query_words = query.lower().split()
                found_count = sum(1 for word in query_words if word in doc_text.lower())
                if found_count > 0:
                    # Get context around the found words
                    for word in query_words:
                        if word in doc_text.lower():
                            idx = doc_text.lower().find(word)
                            context = doc_text[max(0, idx-200):min(len(doc_text), idx+200)]
                            relevant_texts.append(f"...{context}...")
            
            if not relevant_texts:
                return "No relevant information found in documents."
            
            # Combine and summarize
            combined_context = "\n\n".join(relevant_texts[:3])  # Take top 3 matches
            
            prompt = f"""Based on the following context from study materials, answer the question.
            If the context doesn't contain enough information, say so clearly.
            
            Question: {query}
            
            Context from study materials:
            {combined_context}
            
            Provide a helpful and accurate answer:
            """
            
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error searching documents: {str(e)}"

def main():
    # Apply custom CSS
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    # Page configuration
    st.set_page_config(
        page_title="AI-Powered Study Assistant 🤖📚",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Header
    st.markdown('<h1 class="main-header">🤖 AI-Powered Study Assistant 📚</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Upload Notes • Generate Questions • Get Explanations • Ace Your Exams</p>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'documents_loaded' not in st.session_state:
        st.session_state.documents_loaded = False
    if 'assistant' not in st.session_state:
        st.session_state.assistant = None
    if 'api_key_valid' not in st.session_state:
        st.session_state.api_key_valid = False
    
    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.header("⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input("Enter Google Gemini API Key:", type="password", 
                               help="Get your API key from https://makersuite.google.com/app/apikey")
        
        if api_key:
            if st.button("Validate API Key", use_container_width=True):
                with st.spinner("Validating API key..."):
                    try:
                        # Test the API key
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel('gemini-2.5-flash')
                        test_response = model.generate_content("Test")
                        st.session_state.assistant = StudyAssistant(api_key)
                        st.success("✅ API Key validated successfully!")
                        st.session_state.api_key_valid = True
                    except Exception as e:
                        st.error(f"❌ Invalid API Key: {str(e)}")
                        st.session_state.api_key_valid = False
            
            if st.session_state.assistant is None:
                st.info("👆 Click 'Validate API Key' to start")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Statistics
        if st.session_state.assistant and st.session_state.assistant.documents:
            st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
            st.header("📊 Statistics")
            st.metric("Documents Loaded", len(st.session_state.assistant.documents))
            st.metric("Total Text", f"{sum(len(d) for d in st.session_state.assistant.document_texts):,} chars")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Tech Stack Info
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.header("🧠 Architecture")
        st.markdown("""
        **Tech Stack:**
        - **Python** + **Streamlit**
        - **Google Gemini 2.0 Flash**
        - **Simple RAG Implementation**
        - **No Complex Dependencies**
        
        **Features:**
        - ✔️ Document Processing
        - ✔️ GATE + College Exam Focus
        - ✔️ Smart Question Generation
        - ✔️ Document-based Q&A
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick Tips
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("**💡 Quick Start:**")
        st.markdown("""
        1. Enter Gemini API Key
        2. Upload study materials
        3. Use any feature instantly!
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content area with tabs
    if st.session_state.assistant and st.session_state.api_key_valid:
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📁 Upload Documents", 
            "📝 Summarize", 
            "❓ Generate Questions", 
            "💡 Explain Topics", 
            "💬 Chat with Docs"
        ])
        
        # Tab 1: Upload Documents
        with tab1:
            st.markdown('<div class="upload-section">', unsafe_allow_html=True)
            st.header("📁 Upload Your Study Materials")
            st.markdown("Supported formats: PDF, DOCX, TXT, MD")
            
            uploaded_files = st.file_uploader(
                "Drag and drop or click to browse",
                type=['pdf', 'docx', 'txt', 'md'],
                accept_multiple_files=True,
                label_visibility="collapsed"
            )
            
            if uploaded_files:
                progress_bar = st.progress(0)
                all_texts = []
                processed_files = []
                
                for i, uploaded_file in enumerate(uploaded_files):
                    with st.spinner(f"Processing {uploaded_file.name}..."):
                        text = st.session_state.assistant.process_uploaded_file(uploaded_file)
                        if text and len(text.strip()) > 100:
                            all_texts.append(text)
                            processed_files.append(uploaded_file.name)
                            st.success(f"✅ {uploaded_file.name} ({len(text):,} chars)")
                        else:
                            st.warning(f"⚠️ {uploaded_file.name} - Content too short or extraction failed")
                    
                    progress_bar.progress((i + 1) / len(uploaded_files))
                
                if all_texts:
                    if st.button("🚀 Process Documents", type="primary", use_container_width=True):
                        st.session_state.assistant.document_texts = all_texts
                        st.session_state.assistant.documents = processed_files
                        st.session_state.documents_loaded = True
                        st.success(f"✅ Successfully processed {len(processed_files)} documents!")
                        st.balloons()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Tab 2: Summarize
        with tab2:
            st.header("📝 Document Summarizer")
            
            if st.session_state.documents_loaded and st.session_state.assistant.document_texts:
                # Let user select which document to summarize
                if len(st.session_state.assistant.documents) > 1:
                    selected_doc = st.selectbox(
                        "Select document to summarize:",
                        st.session_state.assistant.documents
                    )
                    doc_index = st.session_state.assistant.documents.index(selected_doc)
                    sample_text = st.session_state.assistant.document_texts[doc_index][:5000]
                else:
                    sample_text = st.session_state.assistant.document_texts[0][:5000]
                
                if st.button("Generate Comprehensive Summary", type="primary", use_container_width=True):
                    with st.spinner("🔍 Analyzing document and generating summary..."):
                        summary = st.session_state.assistant.summarize_document(sample_text)
                        
                        st.markdown('<div class="success-box">', unsafe_allow_html=True)
                        st.subheader("📋 Document Summary")
                        st.markdown(summary)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Download option
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            st.download_button(
                                label="📥 Download Summary",
                                data=summary,
                                file_name="document_summary.md",
                                mime="text/markdown",
                                use_container_width=True
                            )
            else:
                st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                st.info("📌 Please upload documents first to generate summaries")
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Tab 3: Generate Questions
        with tab3:
            st.header("❓ Generate Exam Questions")
            
            if st.session_state.documents_loaded and st.session_state.assistant.document_texts:
                col1, col2 = st.columns(2)
                with col1:
                    num_questions = st.slider("Number of questions", 3, 10, 5)
                with col2:
                    question_type = st.selectbox(
                        "Question type",
                        ["Mixed", "Multiple Choice", "Short Answer", "Problem Solving"]
                    )
                
                if st.button("Generate Practice Questions", type="primary", use_container_width=True):
                    with st.spinner("🎯 Generating exam questions..."):
                        sample_text = st.session_state.assistant.document_texts[0][:4000]
                        questions = st.session_state.assistant.generate_questions(
                            sample_text, 
                            num_questions,
                            question_type
                        )
                        
                        for i, q in enumerate(questions, 1):
                            if 'error' in q:
                                st.error(q['error'])
                                continue
                                
                            with st.expander(f"📝 Question {i} | {q.get('type', 'N/A')} | {q.get('difficulty', 'N/A')} | Topic: {q.get('topic', 'N/A')}"):
                                st.markdown(f"**{q.get('question', '')}**")
                                
                                if q.get('options'):
                                    st.write("**Options:**")
                                    for opt in q['options']:
                                        st.write(f"- {opt}")
                                
                                if q.get('answer'):
                                    st.markdown("---")
                                    st.success(f"**Answer:** {q['answer']}")
            else:
                st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                st.info("📌 Please upload documents first to generate questions")
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Tab 4: Explain Topics
        with tab4:
            st.header("💡 Topic Explainer")
            
            topic = st.text_input("Enter a topic you want explained (e.g., 'Machine Learning', 'Quantum Mechanics', 'Thermodynamics'):")
            
            if topic:
                if st.button("Explain This Topic", type="primary", use_container_width=True):
                    with st.spinner(f"🧠 Explaining '{topic}' in simple terms..."):
                        explanation = st.session_state.assistant.explain_topic(topic)
                        
                        st.markdown('<div class="success-box">', unsafe_allow_html=True)
                        st.subheader(f"📚 Explanation: {topic}")
                        st.markdown(explanation)
                        st.markdown('</div>', unsafe_allow_html=True)
        
        # Tab 5: Chat with Documents
        with tab5:
            st.header("💬 Chat with Your Documents")
            
            if st.session_state.documents_loaded:
                # Display chat messages
                for message in st.session_state.messages:
                    if message["role"] == "user":
                        st.markdown(f'<div class="chat-message-user">👤 **You:** {message["content"]}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="chat-message-assistant">🤖 **Assistant:** {message["content"]}</div>', unsafe_allow_html=True)
                
                # Chat input
                if prompt := st.chat_input("Ask a question about your documents..."):
                    # Add user message
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    st.markdown(f'<div class="chat-message-user">👤 **You:** {prompt}</div>', unsafe_allow_html=True)
                    
                    # Get response
                    with st.spinner("🤔 Searching documents..."):
                        response = st.session_state.assistant.search_in_documents(prompt)
                        st.markdown(f'<div class="chat-message-assistant">🤖 **Assistant:** {response}</div>', unsafe_allow_html=True)
                    
                    # Add assistant message
                    st.session_state.messages.append({"role": "assistant", "content": response})
                
                # Clear chat button
                if st.session_state.messages:
                    if st.button("Clear Chat History", use_container_width=True):
                        st.session_state.messages = []
                        st.rerun()
            else:
                st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                st.info("📌 Please upload documents first to enable chat functionality")
                st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        # Welcome screen when no API key is set
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.header("Welcome to AI Study Assistant! 🎓")
        st.markdown("""
        ### Get Started in 3 Simple Steps:
        
        1. **Get API Key** 
           - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
           - Create a free API key
        
        2. **Enter API Key** 
           - Paste your API key in the sidebar
           - Click 'Validate API Key'
        
        3. **Upload Documents & Start Learning!**
        
        ### Features You'll Get:
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            - 📚 **Document Processing (PDF/DOCX/TXT)**
            - 🎯 **Exam Question Generation**
            - 💡 **Topic Explanations**
            - 🔍 **Document Search**
            """)
        with col2:
            st.markdown("""
            - 📊 **Auto Summarization**
            - 💬 **Document Q&A**
            - 📝 **GATE/College Focus**
            - 🚀 **No Complex Setup**
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Architecture diagram
        st.markdown("---")
        st.subheader("🏗️ System Architecture")
        
        st.markdown("""
        ```
        User → Upload Documents → Text Extraction → Gemini AI → Responses
                    ↓
            Summarization / Q&A / Explanations
                    ↓
            Instant Study Assistance
        ```
        """)

if __name__ == "__main__":
    main()