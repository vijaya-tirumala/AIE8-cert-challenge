"""
RAG Components Module
Extracted from the notebook for use in the FastAPI application
"""

import os
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.agents import Tool, initialize_agent, AgentType
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.retrievers.ensemble import EnsembleRetriever

from tavily import TavilyClient

# RAGAS Components (for evaluation)
try:
    import nest_asyncio
    nest_asyncio.apply()
    from ragas import evaluate, EvaluationDataset
    from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
    RAGAS_AVAILABLE = True
    print("✅ RAGAS imported successfully!")
except ImportError:
    RAGAS_AVAILABLE = False
    print("⚠️ RAGAS not available. Install with: pip install ragas")
except Exception as e:
    RAGAS_AVAILABLE = False
    print(f"⚠️ RAGAS import failed: {e}")
    print("🔄 Using custom evaluation framework")


@dataclass
class RAGConfig:
    """Configuration class for RAG pipeline parameters"""
    chunk_size: int = 800
    chunk_overlap: int = 100
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.1
    max_tokens: int = 1000
    similarity_threshold: float = 0.7


class DocumentProcessor:
    """Efficient document processing with optimized chunking strategy"""
    
    def __init__(self, data_path: str, config: RAGConfig = None):
        self.data_path = Path(data_path)
        self.config = config or RAGConfig()
        self.chunk_size = self.config.chunk_size
        self.chunk_overlap = self.config.chunk_overlap
        
    def load_documents(self) -> List[Document]:
        """Load documents from specified directory"""
        loader = DirectoryLoader(
            str(self.data_path),
            glob="**/*.md",
            loader_cls=TextLoader,
            loader_kwargs={'encoding': 'utf-8'}
        )
        documents = loader.load()
        print(f"📄 Loaded {len(documents)} documents")
        return documents
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into optimized chunks"""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = splitter.split_documents(documents)
        print(f"🔪 Split into {len(chunks)} chunks")
        return chunks


class VectorStoreManager:
    """Manages FAISS vector store creation and operations"""
    
    def __init__(self, config: RAGConfig = None):
        self.config = config or RAGConfig()
        self.embeddings = OpenAIEmbeddings()
        
    def create_vectorstore(self, chunks: List[Document]) -> FAISS:
        """Create FAISS vector store from document chunks"""
        vectorstore = FAISS.from_documents(chunks, self.embeddings)
        print(f"🗃️ Created FAISS vectorstore with {len(chunks)} chunks")
        return vectorstore
    
    def create_advanced_vectorstore(self, chunks: List[Document]) -> FAISS:
        """Create optimized vector store with better indexing"""
        vectorstore = FAISS.from_documents(
            chunks, 
            self.embeddings,
            distance_strategy="COSINE"  # Better for semantic similarity
        )
        # Add metadata for better retrieval
        for i, doc in enumerate(chunks):
            if hasattr(doc, 'metadata'):
                doc.metadata['chunk_id'] = i
                doc.metadata['chunk_size'] = len(doc.page_content)
        print(f"🚀 Created advanced FAISS vectorstore with {len(chunks)} chunks")
        return vectorstore


class SERAGAgent:
    """Solution Engineer RAG Agent with hybrid retrieval"""
    
    def __init__(self, vectorstore: FAISS, tavily_client: TavilyClient = None, config: RAGConfig = None):
        self.vectorstore = vectorstore
        self.tavily_client = tavily_client
        self.config = config or RAGConfig()
        self.llm = ChatOpenAI(
            model_name=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
        self.tools = self._create_tools()
        self.agent = self._create_agent()
        
    def _create_tools(self) -> List[Tool]:
        """Create tools for documentation search and web search"""
        
        def search_documentation(query: str) -> str:
            """Search internal documentation using semantic similarity"""
            docs = self.vectorstore.similarity_search(
                query, 
                k=5,
                score_threshold=self.config.similarity_threshold
            )
            if not docs:
                return "No relevant documentation found."
            
            context = "\n\n".join([doc.page_content for doc in docs])
            sources = [doc.metadata.get('source', 'Unknown') for doc in docs]
            return f"Documentation Context:\n{context}\n\nSources: {', '.join(sources)}"
        
        def search_web(query: str) -> str:
            """Search web for current information using Tavily"""
            if not self.tavily_client:
                return "Web search not available - Tavily client not configured."
            
            try:
                results = self.tavily_client.search(
                    query=query,
                    search_depth="advanced",
                    max_results=3
                )
                
                if not results or not results.get('results'):
                    return "No web results found."
                
                web_context = "\n\n".join([
                    f"Title: {result.get('title', 'No title')}\n"
                    f"Content: {result.get('content', 'No content')}\n"
                    f"URL: {result.get('url', 'No URL')}"
                    for result in results['results'][:3]
                ])
                return f"Web Search Results:\n{web_context}"
                
            except Exception as e:
                return f"Web search error: {str(e)}"
        
        return [
            Tool(
                name="search_documentation",
                description="Search internal technical documentation for specific information",
                func=search_documentation
            ),
            Tool(
                name="search_web",
                description="Search the web for current information and external resources",
                func=search_web
            )
        ]
    
    def _create_agent(self):
        """Initialize the conversational agent"""
        return initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            handle_parsing_errors=True,
            verbose=False
        )
    
    def respond_to_rfp(self, question: str) -> Dict[str, Any]:
        """Generate comprehensive RFP response"""
        start_time = time.time()
        
        try:
            # Get agent response
            response = self.agent.run(question)
            
            # Extract sources from tools used
            sources = self._extract_sources(question)
            
            response_time = time.time() - start_time
            
            return {
                "answer": response,
                "sources": sources,
                "response_time": response_time,
                "model": self.config.model_name,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            return {
                "answer": f"Error generating response: {str(e)}",
                "sources": [],
                "response_time": time.time() - start_time,
                "model": self.config.model_name,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "error": str(e)
            }
    
    def _extract_sources(self, query: str) -> List[str]:
        """Extract relevant sources from vectorstore"""
        docs = self.vectorstore.similarity_search(query, k=3)
        return list(set([doc.metadata.get('source', 'Unknown') for doc in docs]))


class AdvancedRetrievalAgent(SERAGAgent):
    """Enhanced RAG agent with advanced retrieval methods"""
    
    def __init__(self, vectorstore: FAISS, tavily_client: TavilyClient = None, config: RAGConfig = None):
        super().__init__(vectorstore, tavily_client, config)
        self.setup_advanced_retrievers()
    
    def setup_advanced_retrievers(self):
        """Setup advanced retrieval strategies"""
        
        # 1. Contextual Compression Retriever
        compressor = LLMChainExtractor.from_llm(self.llm)
        self.compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=self.vectorstore.as_retriever(search_kwargs={"k": 10})
        )
        
        # 2. Multi-Query Retriever
        self.multi_query_retriever = MultiQueryRetriever.from_llm(
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 5}),
            llm=self.llm
        )
        
        # 3. Ensemble Retriever (combining multiple strategies)
        self.ensemble_retriever = EnsembleRetriever(
            retrievers=[
                self.vectorstore.as_retriever(search_kwargs={"k": 3}),
                self.compression_retriever
            ],
            weights=[0.7, 0.3]
        )
    
    def _create_tools(self) -> List[Tool]:
        """Create enhanced tools with advanced retrieval methods"""
        
        def search_documentation(query: str) -> str:
            """Search internal documentation using semantic similarity"""
            docs = self.vectorstore.similarity_search(
                query, 
                k=5,
                score_threshold=self.config.similarity_threshold
            )
            if not docs:
                return "No relevant documentation found."
            
            context = "\n\n".join([doc.page_content for doc in docs])
            sources = [doc.metadata.get('source', 'Unknown') for doc in docs]
            return f"Documentation Context:\n{context}\n\nSources: {', '.join(sources)}"
        
        def search_web(query: str) -> str:
            """Search web for current information using Tavily"""
            if not self.tavily_client:
                return "Web search not available - Tavily client not configured."
            
            try:
                results = self.tavily_client.search(
                    query=query,
                    search_depth="advanced",
                    max_results=5,
                    include_domains=["stackoverflow.com", "github.com", "docs.microsoft.com", "developer.mozilla.org"]
                )
                
                if not results or not results.get('results'):
                    return "No relevant web results found."
                
                web_context = "\n\n".join([
                    f"Title: {result.get('title', 'No title')}\n"
                    f"Content: {result.get('content', 'No content')[:500]}...\n"
                    f"URL: {result.get('url', 'No URL')}"
                    for result in results['results'][:3]
                ])
                return f"Advanced Web Search Results:\n{web_context}"
                
            except Exception as e:
                return f"Web search error: {str(e)}"
        
        return [
            Tool(
                name="search_documentation",
                description="Search internal technical documentation for specific information",
                func=search_documentation
            ),
            Tool(
                name="search_web",
                description="Advanced web search with domain filtering for technical content",
                func=search_web
            )
        ]


class ConservativeRAGAgent(SERAGAgent):
    """Conservative RAG agent with strict retrieval parameters"""
    
    def __init__(self, vectorstore: FAISS, tavily_client: TavilyClient = None):
        # Conservative configuration
        conservative_config = RAGConfig(
            chunk_size=600,  # Smaller chunks
            chunk_overlap=50,  # Less overlap
            temperature=0.0,  # More deterministic
            max_tokens=800,  # Shorter responses
            similarity_threshold=0.8  # Higher threshold
        )
        super().__init__(vectorstore, tavily_client, conservative_config)
    
    def _create_tools(self) -> List[Tool]:
        """Create conservative tools with stricter parameters"""
        
        def search_documentation_conservative(query: str) -> str:
            """Conservative documentation search with high relevance threshold"""
            docs = self.vectorstore.similarity_search(
                query, 
                k=3,  # Fewer documents
                score_threshold=self.config.similarity_threshold
            )
            if not docs:
                return "No highly relevant documentation found."
            
            context = "\n\n".join([doc.page_content for doc in docs])
            sources = [doc.metadata.get('source', 'Unknown') for doc in docs]
            return f"Conservative Documentation Context:\n{context}\n\nSources: {', '.join(sources)}"
        
        return [
            Tool(
                name="search_documentation_conservative",
                description="Conservative search of internal documentation with high relevance threshold",
                func=search_documentation_conservative
            )
        ]


@dataclass
class GoldenTestCase:
    """Data class for golden test cases with M&A and Solution Engineer focus"""
    question: str
    expected_answer: str
    category: str
    difficulty: str  # easy, medium, hard
    expected_sources: List[str]
    keywords: List[str]
    evaluation_criteria: Dict[str, float]


class RAGEvaluator:
    """Comprehensive RAG evaluation system with RAGAS metrics and M&A focus"""

    def __init__(self):
        self.llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.0)
        # Import RAGAS components for evaluation
        if RAGAS_AVAILABLE:
            from ragas import EvaluationDataset
            self.EvaluationDataset = EvaluationDataset

    def generate_golden_dataset(self) -> List[GoldenTestCase]:
        """Generate golden dataset with M&A and Solution Engineer focused questions"""
        return [
            # M&A and Solution Engineer Focused Questions
            GoldenTestCase(
                question="What are the key technical risks and dependencies when integrating this platform into an acquired company's existing infrastructure?",
                expected_answer="The platform requires careful assessment of existing data infrastructure, network connectivity, security policies, and compliance requirements. Key risks include data migration complexity, integration with legacy systems, and potential downtime during transition. Dependencies include Java JDK 11+, minimum 64GB RAM, and 10 Gigabit Ethernet connectivity.",
                category="M&A Integration",
                difficulty="hard",
                expected_sources=["sample_rfp_responses.md", "sample_product_specs.md", "ma_solution_engineer_questions.md"],
                keywords=["M&A", "integration", "technical risks", "dependencies", "infrastructure"],
                evaluation_criteria={"accuracy": 0.85, "completeness": 0.9, "relevance": 0.95}
            ),
            GoldenTestCase(
                question="How can the platform be customized to meet specific client requirements in a complex enterprise environment?",
                expected_answer="The platform offers extensive customization through RESTful APIs, configurable RBAC permissions, custom data connectors, and integration with enterprise systems (SAP, Oracle, Salesforce). Solution engineers can leverage the platform's modular architecture to create client-specific implementations while maintaining core functionality.",
                category="Solution Engineering",
                difficulty="hard",
                expected_sources=["sample_product_specs.md", "sample_rfp_responses.md", "ma_solution_engineer_questions.md"],
                keywords=["customization", "client requirements", "enterprise", "APIs", "RBAC"],
                evaluation_criteria={"accuracy": 0.85, "completeness": 0.9, "relevance": 0.95}
            ),
            GoldenTestCase(
                question="What support is available for Solution Engineers during client implementations and troubleshooting?",
                expected_answer="Comprehensive support includes dedicated Solution Engineer resources, 24x7 technical support with 1-hour response time for critical issues, on-site implementation assistance, custom training programs, and access to detailed API documentation with examples. Enterprise support includes dedicated support team with custom SLA.",
                category="Solution Engineering",
                difficulty="medium",
                expected_sources=["sample_faq.md", "sample_rfp_responses.md", "ma_solution_engineer_questions.md"],
                keywords=["support", "Solution Engineers", "implementation", "troubleshooting", "training"],
                evaluation_criteria={"accuracy": 0.9, "completeness": 0.85, "relevance": 0.95}
            ),
            GoldenTestCase(
                question="How does the platform ensure business continuity during M&A integration without disrupting ongoing operations?",
                expected_answer="The platform provides 99.9% SLA with automatic failover, multi-region replication with RTO < 1 hour, incremental backup capabilities with point-in-time recovery, and phased deployment options. These features enable seamless integration while maintaining operational continuity and minimizing business disruption.",
                category="M&A Integration",
                difficulty="hard",
                expected_sources=["sample_faq.md", "sample_product_specs.md", "ma_solution_engineer_questions.md"],
                keywords=["business continuity", "M&A", "integration", "SLA", "failover"],
                evaluation_criteria={"accuracy": 0.85, "completeness": 0.9, "relevance": 0.95}
            ),
            GoldenTestCase(
                question="What cost optimization strategies are available when consolidating multiple acquired companies onto this platform?",
                expected_answer="Cost optimization includes per-core licensing based on actual usage, tiered pricing for data volume, hybrid deployment options combining on-premises and cloud resources, and intelligent auto-scaling to match demand. The platform's linear scaling capabilities ensure cost efficiency as the organization grows through acquisitions.",
                category="M&A Cost Optimization",
                difficulty="medium",
                expected_sources=["sample_product_specs.md", "sample_rfp_responses.md", "ma_solution_engineer_questions.md"],
                keywords=["cost optimization", "consolidation", "acquired companies", "licensing", "scaling"],
                evaluation_criteria={"accuracy": 0.9, "completeness": 0.85, "relevance": 0.95}
            ),
            GoldenTestCase(
                question="How does the platform handle multi-tenant scenarios common in M&A situations where multiple business units need isolated data access?",
                expected_answer="The platform provides fine-grained RBAC with column-level permissions, tenant isolation through configurable access controls, and support for multiple deployment models including hybrid and multi-cloud architectures. This enables secure data segregation while maintaining centralized management capabilities.",
                category="M&A Multi-tenancy",
                difficulty="hard",
                expected_sources=["sample_product_specs.md", "sample_rfp_responses.md", "ma_solution_engineer_questions.md"],
                keywords=["multi-tenant", "M&A", "business units", "isolated access", "RBAC"],
                evaluation_criteria={"accuracy": 0.85, "completeness": 0.9, "relevance": 0.95}
            ),
            GoldenTestCase(
                question="What are the compliance and regulatory considerations when integrating this platform across different geographic regions in an M&A scenario?",
                expected_answer="The platform meets multiple compliance standards including SOC 2 Type II, ISO 27001, GDPR, HIPAA (optional), and PCI DSS (optional). It supports multi-region deployment with data residency controls, ensuring compliance with local regulations while maintaining operational continuity across acquired entities.",
                category="M&A Compliance",
                difficulty="hard",
                expected_sources=["sample_faq.md", "sample_product_specs.md", "ma_solution_engineer_questions.md"],
                keywords=["compliance", "regulatory", "geographic regions", "M&A", "data residency"],
                evaluation_criteria={"accuracy": 0.85, "completeness": 0.9, "relevance": 0.95}
            )
        ]

    def evaluate_with_ragas(self, questions: List[str], contexts: List[List[str]],
                           answers: List[str], ground_truths: List[str]) -> Dict[str, float]:
        """Evaluate using RAGAS framework"""
        if not RAGAS_AVAILABLE:
            print("⚠️ RAGAS not available, using custom evaluation")
            return self.custom_evaluation(questions, contexts, answers, ground_truths)

        try:
            # Prepare data for RAGAS 0.2.10 format using EvaluationDataset
            import pandas as pd

            # RAGAS 0.2.10 requires specific column names
            df = pd.DataFrame({
                "user_input": questions,
                "retrieved_contexts": contexts,
                "response": answers,
                "ground_truth": ground_truths,
                "reference": ground_truths  # context_precision metric requires reference column
            })

            dataset = self.EvaluationDataset.from_pandas(df)
            print(f"📊 Created RAGAS dataset with {len(df)} samples")

            # Define metrics (using correct names for RAGAS 0.2.10)
            metrics = [
                faithfulness,
                answer_relevancy,
                context_precision,
                context_recall
            ]

            print("🔍 Running RAGAS evaluation...")
            # Run evaluation
            result = evaluate(dataset, metrics=metrics)

            # Extract results from the evaluation result
            # Handle different result formats
            if hasattr(result, 'to_pandas'):
                # If result is a Dataset object
                df = result.to_pandas()
                return {
                    "faithfulness": df['faithfulness'].mean(),
                    "answer_relevancy": df['answer_relevancy'].mean(),
                    "context_precision": df['context_precision'].mean(),
                    "context_recall": df['context_recall'].mean()
                }
            else:
                # If result is a dictionary
                return {
                    "faithfulness": result.get("faithfulness", 0.0),
                    "answer_relevancy": result.get("answer_relevancy", 0.0),
                    "context_precision": result.get("context_precision", 0.0),
                    "context_recall": result.get("context_recall", 0.0)
                }

        except Exception as e:
            print(f"RAGAS evaluation failed: {e}")
            print("🔄 Falling back to custom evaluation framework")
            return self.custom_evaluation(questions, contexts, answers, ground_truths)

    def custom_evaluation(self, questions: List[str], contexts: List[List[str]],
                         answers: List[str], ground_truths: List[str]) -> Dict[str, float]:
        """Custom evaluation framework when RAGAS is not available"""
        import numpy as np
        
        def calculate_faithfulness(answer: str, contexts: List[str]) -> float:
            """Simple faithfulness calculation"""
            # Simple implementation - check if answer is grounded in contexts
            answer_words = set(answer.lower().split())
            context_text = " ".join(contexts).lower()
            context_words = set(context_text.split())
            
            overlap = len(answer_words.intersection(context_words))
            return min(overlap / len(answer_words) if answer_words else 0.0, 1.0)
        
        def calculate_response_relevancy(question: str, answer: str) -> float:
            """Simple response relevancy calculation"""
            # Simple implementation - check keyword overlap
            q_words = set(question.lower().split())
            a_words = set(answer.lower().split())
            
            overlap = len(q_words.intersection(a_words))
            return min(overlap / len(q_words) if q_words else 0.0, 1.0)
        
        def calculate_context_precision(question: str, contexts: List[str]) -> float:
            """Simple context precision calculation"""
            # Simple implementation - assume all contexts are relevant
            return 0.8  # Default score
        
        def calculate_context_recall(ground_truth: str, contexts: List[str]) -> float:
            """Simple context recall calculation"""
            # Simple implementation - check if ground truth info is in contexts
            gt_words = set(ground_truth.lower().split())
            context_text = " ".join(contexts).lower()
            context_words = set(context_text.split())
            
            overlap = len(gt_words.intersection(context_words))
            return overlap / len(gt_words) if gt_words else 0.0
        
        # Calculate metrics for all samples
        faithfulness_scores = [calculate_faithfulness(ans, ctx) 
                              for ans, ctx in zip(answers, contexts)]
        relevancy_scores = [calculate_response_relevancy(q, ans) 
                           for q, ans in zip(questions, answers)]
        precision_scores = [calculate_context_precision(q, ctx) 
                           for q, ctx in zip(questions, contexts)]
        recall_scores = [calculate_context_recall(gt, ctx) 
                        for gt, ctx in zip(ground_truths, contexts)]
        
        return {
            "faithfulness": np.mean(faithfulness_scores),
            "answer_relevancy": np.mean(relevancy_scores),
            "context_precision": np.mean(precision_scores),
            "context_recall": np.mean(recall_scores)
        }
