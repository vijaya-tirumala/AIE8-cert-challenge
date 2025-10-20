# SolvIQ RAG Components Architecture

## 🔧 RAG Components & Tools Graph

```mermaid
graph TD
    %% Configuration Layer
    A[RAGConfig] --> B[DocumentProcessor]
    A --> C[VectorStoreManager]
    A --> D[SERAGAgent]
    
    %% Document Processing Pipeline
    B --> E[DirectoryLoader]
    B --> F[TextLoader]
    B --> G[RecursiveCharacterTextSplitter]
    
    %% Vector Store Management
    C --> H[FAISS Vector Store]
    C --> I[OpenAI Embeddings]
    
    %% Base RAG Agent
    D --> J[ChatOpenAI - GPT-4o-mini]
    D --> K[RetrievalQA Chain]
    D --> L[Tavily Web Search]
    D --> M[LangChain Agents]
    
    %% Advanced Retrieval Methods
    N[AdvancedRetrievalAgent] --> O[ContextualCompressionRetriever]
    N --> P[MultiQueryRetriever]
    N --> Q[EnsembleRetriever]
    N --> R[LLMChainExtractor]
    
    %% Conservative Agent
    S[ConservativeRAGAgent] --> T[Strict Thresholds]
    S --> U[High Precision Mode]
    
    %% Evaluation Framework
    V[RAGEvaluator] --> W[RAGAS Metrics]
    V --> X[GoldenTestCase]
    V --> Y[Custom Evaluation]
    
    %% RAGAS Metrics
    W --> Z[Faithfulness]
    W --> AA[Answer Relevancy]
    W --> BB[Context Precision]
    W --> CC[Context Recall]
    
    %% Inheritance
    D --> N
    D --> S
    
    %% Data Flow
    E --> G
    F --> G
    G --> H
    I --> H
    H --> K
    J --> K
    L --> M
    K --> M
    
    %% Advanced Retrieval Flow
    O --> R
    P --> Q
    Q --> K
    
    %% Styling
    classDef configClass fill:#e1f5fe
    classDef agentClass fill:#f3e5f5
    classDef retrievalClass fill:#e8f5e8
    classDef evalClass fill:#fff3e0
    classDef toolClass fill:#fce4ec
    
    class A,RAGConfig configClass
    class D,SERAGAgent,N,AdvancedRetrievalAgent,S,ConservativeRAGAgent agentClass
    class O,ContextualCompressionRetriever,P,MultiQueryRetriever,Q,EnsembleRetriever retrievalClass
    class V,RAGEvaluator,W,RAGAS Metrics evalClass
    class E,DirectoryLoader,F,TextLoader,G,RecursiveCharacterTextSplitter,H,FAISS Vector Store,I,OpenAI Embeddings,J,ChatOpenAI - GPT-4o-mini,K,RetrievalQA Chain,L,Tavily Web Search,M,LangChain Agents toolClass
```

## 📊 Component Categories

### 🔧 **Configuration & Core Classes**
- **RAGConfig**: Central configuration for all RAG parameters
- **DocumentProcessor**: Handles document loading and chunking
- **VectorStoreManager**: Manages FAISS vector store operations
- **GoldenTestCase**: Data structure for evaluation test cases

### 🤖 **RAG Agent Classes**
- **SERAGAgent**: Base RAG agent with standard retrieval
- **AdvancedRetrievalAgent**: Enhanced retrieval with multiple strategies
- **ConservativeRAGAgent**: High-precision retrieval with strict thresholds

### 🔍 **Retrieval Methods**
- **ContextualCompressionRetriever**: Compresses retrieved documents
- **MultiQueryRetriever**: Generates multiple query variations
- **EnsembleRetriever**: Combines multiple retrieval strategies
- **LLMChainExtractor**: Extracts relevant information using LLM

### 📈 **Evaluation Framework**
- **RAGEvaluator**: Comprehensive evaluation system
- **RAGAS Metrics**: Industry-standard evaluation metrics
- **Custom Evaluation**: Fallback evaluation methods

### 🛠️ **External Tools & APIs**
- **FAISS**: Vector similarity search
- **OpenAI Embeddings**: Text vectorization
- **ChatOpenAI**: Language model for response generation
- **Tavily**: Web search integration
- **LangChain**: Orchestration framework

## 🔄 **Data Flow Process**

1. **Document Ingestion**: DirectoryLoader → TextLoader → RecursiveCharacterTextSplitter
2. **Vectorization**: OpenAI Embeddings → FAISS Vector Store
3. **Query Processing**: User Query → Retrieval Methods → Context Retrieval
4. **Response Generation**: Retrieved Context → ChatOpenAI → Final Response
5. **Evaluation**: Generated Response → RAGAS Metrics → Performance Assessment

## 🎯 **Key Features**

- **Multi-Agent Architecture**: Three specialized RAG agents for different use cases
- **Advanced Retrieval**: Contextual compression, multi-query, and ensemble methods
- **Comprehensive Evaluation**: RAGAS framework with custom fallback
- **Web Search Integration**: Tavily API for external knowledge
- **Production Ready**: Structured logging, error handling, and configuration management
