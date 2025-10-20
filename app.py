"""
FastAPI Backend for SE RAG Agent
Provides REST API endpoints for the RAG system
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("solviq.log")
    ]
)
logger = logging.getLogger(__name__)

# Import our RAG components from the module
try:
    from rag_components import (
        SERAGAgent,
        AdvancedRetrievalAgent,
        ConservativeRAGAgent,
        RAGConfig,
        DocumentProcessor,
        VectorStoreManager,
        RAGEvaluator,
        GoldenTestCase
    )
    from tavily import TavilyClient
    logger.info("RAG components imported successfully")
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.error("Make sure rag_components.py is in the project root directory")
    sys.exit(1)

app = FastAPI(
    title="SolvIQ API",
    description="The intelligence layer for every Solution Engineer - Your AI-powered RFP response partner.",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for RAG components
vectorstore = None
standard_agent = None
advanced_agent = None
conservative_agent = None
config = None

async def initialize_rag_components():
    """Initialize RAG components on startup"""
    global vectorstore, standard_agent, advanced_agent, conservative_agent, config
    
    try:
        logger.info("Initializing RAG components...")
        
        # Set up configuration
        config = RAGConfig()
        logger.info(f"Configuration loaded: {config}")
        
        # Process documents
        from config import get_data_path
        data_path = get_data_path()
        if not data_path.exists():
            raise FileNotFoundError(f"Data directory not found: {data_path}")
            
        processor = DocumentProcessor(str(data_path), config)
        documents = processor.load_documents()
        logger.info(f"Loaded {len(documents)} documents")
        
        if not documents:
            raise ValueError("No documents loaded from data directory")
        
        # Create vector store
        vector_manager = VectorStoreManager()
        vectorstore = vector_manager.create_vectorstore(documents)
        logger.info("Vector store created successfully")
        
        # Initialize agents
        standard_agent = SERAGAgent(vectorstore, config)
        advanced_agent = AdvancedRetrievalAgent(vectorstore, config)
        conservative_agent = ConservativeRAGAgent(vectorstore, config)
        
        logger.info("All RAG agents initialized successfully")
        logger.info("SolvIQ is ready as the intelligence layer for Solution Engineers!")
        
    except Exception as e:
        logger.error(f"Error initializing RAG components: {e}")
        logger.exception("Full traceback:")
        raise HTTPException(status_code=500, detail=f"Failed to initialize RAG components: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    await initialize_rag_components()

class QueryRequest(BaseModel):
    question: str
    agent_type: str = "advanced"  # "standard", "advanced", "conservative"

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    response_time: float
    agent_type: str
    model: str

@app.on_event("startup")
async def startup_event():
    """Initialize RAG components on startup"""
    global vectorstore, standard_agent, advanced_agent, conservative_agent
    
    try:
        print("🚀 Initializing SE RAG Agent API...")
        
        # Check for API keys
        if not os.environ.get("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable not set")
        if not os.environ.get("TAVILY_API_KEY"):
            raise ValueError("TAVILY_API_KEY environment variable not set")
        
        # Configuration
        config = RAGConfig()
        from config import get_data_path
        data_path = str(get_data_path())
        
        # Document processing
        processor = DocumentProcessor(data_path, config)
        documents = processor.load_documents()
        chunks = processor.chunk_documents(documents)
        
        # Vector store creation
        vector_manager = VectorStoreManager(config)
        vectorstore = vector_manager.create_advanced_vectorstore(chunks)
        
        # Tavily client
        tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
        
        # Initialize agents
        standard_agent = SERAGAgent(vectorstore, tavily_client, config)
        advanced_agent = AdvancedRetrievalAgent(vectorstore, tavily_client, config)
        conservative_agent = ConservativeRAGAgent(vectorstore, tavily_client)
        
        print("✅ SolvIQ API initialized successfully!")
        print("⚡ SolvIQ is ready as the intelligence layer for Solution Engineers!")
        
    except Exception as e:
        print(f"❌ Failed to initialize RAG components: {e}")
        raise e

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "⚡ SolvIQ API",
        "description": "The intelligence layer for every Solution Engineer - Your AI-powered RFP response partner.",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "query": "/query",
            "health": "/health",
            "agents": "/agents",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "components": {
            "vectorstore": vectorstore is not None,
            "standard_agent": standard_agent is not None,
            "advanced_agent": advanced_agent is not None,
            "conservative_agent": conservative_agent is not None
        }
    }

@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """Query the RAG system"""
    try:
        # Select agent based on type
        if request.agent_type == "standard":
            agent = standard_agent
        elif request.agent_type == "advanced":
            agent = advanced_agent
        elif request.agent_type == "conservative":
            agent = conservative_agent
        else:
            raise HTTPException(status_code=400, detail="Invalid agent_type. Use 'standard', 'advanced', or 'conservative'")
        
        if not agent:
            raise HTTPException(status_code=500, detail="Agent not initialized")
        
        # Get response
        response = agent.respond_to_rfp(request.question)
        
        return QueryResponse(
            answer=response["answer"],
            sources=response["sources"],
            response_time=response["response_time"],
            agent_type=request.agent_type,
            model=response["model"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/agents")
async def list_agents():
    """List available agents"""
    return {
        "available_agents": [
            {
                "type": "standard",
                "description": "RAG agent with basic retrieval",
                "features": ["Technical document search", "Web search", "Basic retrieval", "Enterprise focus"],
                "chunk_size": 800,
                "chunk_overlap": 100
            },
            {
                "type": "advanced",
                "description": "RAG agent with enhanced retrieval methods",
                "features": ["Contextual compression", "Multi-query retrieval", "Ensemble methods", "Enterprise domain filtering"],
                "chunk_size": 800,
                "chunk_overlap": 100
            },
            {
                "type": "conservative",
                "description": "RAG agent with strict parameters",
                "features": ["High precision", "Strict thresholds", "Reliable enterprise responses", "Compliance focus"],
                "chunk_size": 600,
                "chunk_overlap": 50
            }
        ]
    }


@app.get("/evaluation/golden-dataset")
async def get_golden_dataset():
    """Get M&A and Solution Engineer focused golden dataset"""
    try:
        evaluator = RAGEvaluator()
        golden_dataset = evaluator.generate_golden_dataset()
        
        # Convert to serializable format
        dataset_data = []
        for test_case in golden_dataset:
            dataset_data.append({
                "question": test_case.question,
                "expected_answer": test_case.expected_answer,
                "category": test_case.category,
                "difficulty": test_case.difficulty,
                "expected_sources": test_case.expected_sources,
                "keywords": test_case.keywords,
                "evaluation_criteria": test_case.evaluation_criteria
            })
        
        return {
            "total_questions": len(dataset_data),
            "categories": list(set([item["category"] for item in dataset_data])),
            "difficulties": list(set([item["difficulty"] for item in dataset_data])),
            "questions": dataset_data
        }
    except Exception as e:
        return {"error": f"Failed to generate golden dataset: {str(e)}"}


@app.post("/evaluation/run")
async def run_evaluation(agent_type: str = "standard"):
    """Run RAGAS evaluation on the golden dataset"""
    try:
        # Initialize evaluator
        evaluator = RAGEvaluator()
        golden_dataset = evaluator.generate_golden_dataset()
        
        # Get the appropriate agent
        if agent_type == "advanced":
            agent = AdvancedRetrievalAgent(vectorstore, config)
        elif agent_type == "conservative":
            agent = ConservativeRAGAgent(vectorstore, config)
        else:
            agent = SERAGAgent(vectorstore, config)
        
        # Prepare evaluation data
        questions = []
        contexts = []
        answers = []
        ground_truths = []
        
        for test_case in golden_dataset[:3]:  # Limit to 3 questions for demo
            # Get response from agent
            response = agent.respond_to_rfp(test_case.question)
            
            # Retrieve context
            retrieved_docs = vectorstore.similarity_search(test_case.question, k=5)
            context = [doc.page_content for doc in retrieved_docs]
            
            # Store results
            questions.append(test_case.question)
            contexts.append(context)
            answers.append(response)
            ground_truths.append(test_case.expected_answer)
        
        # Run evaluation
        metrics = evaluator.evaluate_with_ragas(questions, contexts, answers, ground_truths)
        
        return {
            "agent_type": agent_type,
            "evaluation_metrics": metrics,
            "questions_evaluated": len(questions),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": f"Evaluation failed: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
