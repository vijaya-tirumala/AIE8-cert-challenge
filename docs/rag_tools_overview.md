# SolvIQ RAG Tools Overview

## 🛠️ Core RAG Tools & Components

```mermaid
graph LR
    %% Input Layer
    A[📄 Documents] --> B[🔧 DocumentProcessor]
    
    %% Processing Layer
    B --> C[✂️ Text Splitter]
    C --> D[🧠 OpenAI Embeddings]
    D --> E[🗄️ FAISS Vector Store]
    
    %% Query Layer
    F[❓ User Query] --> G[🔍 Retrieval Methods]
    G --> E
    E --> H[📋 Retrieved Context]
    
    %% Generation Layer
    H --> I[🤖 ChatOpenAI GPT-4o-mini]
    I --> J[💬 Generated Response]
    
    %% Advanced Retrieval
    K[🔧 AdvancedRetrievalAgent] --> L[📊 Contextual Compression]
    K --> M[🔄 Multi-Query]
    K --> N[🎯 Ensemble Methods]
    
    %% Evaluation Layer
    J --> O[📈 RAGEvaluator]
    O --> P[🎯 RAGAS Metrics]
    
    %% Web Search Integration
    Q[🌐 Tavily API] --> R[🔍 Web Search]
    R --> I
    
    %% Styling
    classDef inputClass fill:#e3f2fd
    classDef processClass fill:#f1f8e9
    classDef queryClass fill:#fff3e0
    classDef outputClass fill:#fce4ec
    classDef evalClass fill:#f3e5f5
    
    class A,Documents,F,User Query inputClass
    class B,DocumentProcessor,C,Text Splitter,D,OpenAI Embeddings,E,FAISS Vector Store processClass
    class G,Retrieval Methods,H,Retrieved Context,K,AdvancedRetrievalAgent,L,Contextual Compression,M,Multi-Query,N,Ensemble Methods queryClass
    class I,ChatOpenAI GPT-4o-mini,J,Generated Response,Q,Tavily API,R,Web Search outputClass
    class O,RAGEvaluator,P,RAGAS Metrics evalClass
```

## 📋 **Tool Categories & Functions**

| Category | Tools | Purpose |
|----------|-------|---------|
| **📄 Document Processing** | DirectoryLoader, TextLoader, RecursiveCharacterTextSplitter | Load and chunk documents for processing |
| **🧠 Embedding & Vectorization** | OpenAI Embeddings, FAISS | Convert text to vectors and store for retrieval |
| **🔍 Retrieval Methods** | Standard, Advanced, Conservative retrievers | Find relevant context for queries |
| **🤖 Language Generation** | ChatOpenAI (GPT-4o-mini), RetrievalQA Chain | Generate responses from retrieved context |
| **🌐 External Knowledge** | Tavily API, Web Search | Supplement internal knowledge with web data |
| **📈 Evaluation** | RAGAS Framework, Custom Metrics | Assess response quality and accuracy |
| **🔧 Orchestration** | LangChain, Agents, Tools | Coordinate all components and workflows |

## 🎯 **Key Tool Relationships**

### **Core RAG Pipeline:**
1. **Documents** → **DocumentProcessor** → **Text Splitter** → **Embeddings** → **Vector Store**
2. **User Query** → **Retrieval Methods** → **Vector Store** → **Retrieved Context**
3. **Retrieved Context** → **ChatOpenAI** → **Generated Response**

### **Advanced Retrieval Enhancement:**
- **Contextual Compression**: Reduces noise in retrieved documents
- **Multi-Query**: Generates multiple query variations for better coverage
- **Ensemble Methods**: Combines multiple retrieval strategies

### **Evaluation & Quality Assurance:**
- **RAGAS Metrics**: Industry-standard evaluation (faithfulness, relevancy, precision, recall)
- **Custom Evaluation**: Fallback methods when RAGAS is unavailable

## 🚀 **Tool Integration Benefits**

- **Modular Design**: Each tool has a specific, well-defined purpose
- **Scalable Architecture**: Easy to swap or upgrade individual components
- **Production Ready**: Built-in error handling and fallback mechanisms
- **Comprehensive Coverage**: From document ingestion to response evaluation
- **Solution Engineer Focus**: Optimized for technical documentation and enterprise use cases
