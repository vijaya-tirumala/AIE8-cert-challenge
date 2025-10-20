# Simple RAG Components Diagram

```mermaid
graph TD
    A[RAGConfig] --> B[DocumentProcessor]
    B --> C[Text Splitter]
    C --> D[OpenAI Embeddings]
    D --> E[FAISS Vector Store]
    
    F[User Query] --> G[SERAGAgent]
    G --> E
    E --> H[Retrieved Context]
    H --> I[ChatOpenAI GPT-4o-mini]
    I --> J[Generated Response]
    
    K[AdvancedRetrievalAgent] --> L[Contextual Compression]
    K --> M[Multi-Query Retrieval]
    K --> N[Ensemble Methods]
    
    O[RAGEvaluator] --> P[RAGAS Metrics]
    P --> Q[Faithfulness]
    P --> R[Answer Relevancy]
    P --> S[Context Precision]
    P --> T[Context Recall]
    
    U[Tavily API] --> V[Web Search]
    V --> I
```

## 🎯 **How to View Mermaid Diagrams:**

### **1. VS Code Extension (Recommended)**
- Install "Mermaid Preview" extension in VS Code
- Open this file and right-click → "Open Preview to the Side"

### **2. GitHub (Automatic)**
- Push to GitHub repository
- View the `.md` files online - diagrams render automatically

### **3. Online Editor**
- Go to [mermaid.live](https://mermaid.live/)
- Copy the mermaid code between ```mermaid and ``` tags
- Paste and view instantly

### **4. Command Line (You have this installed)**
```bash
mmdc -i docs/simple_rag_diagram.md -o docs/simple_rag_diagram.png
```
