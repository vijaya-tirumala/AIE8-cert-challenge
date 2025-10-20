#!/usr/bin/env python3
"""
Run RAGAS Evaluation Script for SolvIQ
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def run_evaluation(agent_type="standard"):
    """Run RAGAS evaluation for specified agent type"""
    
    try:
        # Import RAG components
        from rag_components import (
            RAGConfig, DocumentProcessor, VectorStoreManager,
            SERAGAgent, AdvancedRetrievalAgent, ConservativeRAGAgent,
            RAGEvaluator
        )
        from config import get_data_path
        
        print(f"🔬 Running RAGAS Evaluation for {agent_type.title()} Agent")
        print("=" * 60)
        
        # Initialize configuration
        config = RAGConfig()
        data_path = get_data_path()
        
        # Load documents and create vector store
        print("📚 Loading documents...")
        processor = DocumentProcessor(str(data_path), config)
        documents = processor.load_documents()
        
        vector_manager = VectorStoreManager()
        vectorstore = vector_manager.create_vectorstore(documents)
        print(f"✅ Loaded {len(documents)} documents")
        
        # Initialize the specified agent
        print(f"🤖 Initializing {agent_type} agent...")
        if agent_type == "advanced":
            agent = AdvancedRetrievalAgent(vectorstore, config)
        elif agent_type == "conservative":
            agent = ConservativeRAGAgent(vectorstore, config)
        else:
            agent = SERAGAgent(vectorstore, config)
        
        # Initialize evaluator
        print("📊 Setting up RAGAS evaluator...")
        evaluator = RAGEvaluator()
        golden_dataset = evaluator.generate_golden_dataset()
        
        # Run evaluation on subset of questions (limit to 3 for demo)
        print(f"🔍 Running evaluation on {min(3, len(golden_dataset))} test cases...")
        
        questions = []
        contexts = []
        answers = []
        ground_truths = []
        
        for i, test_case in enumerate(golden_dataset[:3]):
            print(f"  Testing {i+1}: {test_case.question[:50]}...")
            
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
        
        # Run RAGAS evaluation
        print("📈 Computing RAGAS metrics...")
        metrics = evaluator.evaluate_with_ragas(questions, contexts, answers, ground_truths)
        
        # Display results
        print("\n🎯 EVALUATION RESULTS")
        print("=" * 40)
        print(f"Agent Type: {agent_type.title()}")
        print(f"Questions Evaluated: {len(questions)}")
        print(f"Faithfulness: {metrics['faithfulness']:.3f}")
        print(f"Answer Relevancy: {metrics['answer_relevancy']:.3f}")
        print(f"Context Precision: {metrics['context_precision']:.3f}")
        print(f"Context Recall: {metrics['context_recall']:.3f}")
        
        overall_score = (metrics['faithfulness'] + metrics['answer_relevancy'] + 
                        metrics['context_precision'] + metrics['context_recall']) / 4
        print(f"Overall Score: {overall_score:.3f}")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"metrics/rag_evaluation_results_{agent_type}_{timestamp}.json"
        
        # Ensure metrics directory exists
        Path("metrics").mkdir(exist_ok=True)
        
        import json
        with open(results_file, 'w') as f:
            json.dump({
                "agent_type": agent_type,
                "timestamp": timestamp,
                "metrics": metrics,
                "overall_score": overall_score,
                "questions_evaluated": len(questions)
            }, f, indent=2)
        
        print(f"\n💾 Results saved to: {results_file}")
        print("✅ Evaluation completed successfully!")
        
        return metrics
        
    except Exception as e:
        print(f"❌ Error running evaluation: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    if len(sys.argv) > 1:
        agent_type = sys.argv[1]
        if agent_type not in ["standard", "advanced", "conservative"]:
            print("❌ Invalid agent type. Use: standard, advanced, or conservative")
            sys.exit(1)
    else:
        agent_type = "standard"
    
    print("🚀 SolvIQ RAGAS Evaluation Runner")
    print("=" * 50)
    
    # Check API keys
    if not os.environ.get("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    if not os.environ.get("TAVILY_API_KEY"):
        print("❌ TAVILY_API_KEY environment variable not set")
        sys.exit(1)
    
    # Run evaluation
    metrics = run_evaluation(agent_type)
    
    if metrics:
        print(f"\n🎉 Evaluation completed for {agent_type} agent!")
    else:
        print(f"\n❌ Evaluation failed for {agent_type} agent!")
        sys.exit(1)

if __name__ == "__main__":
    main()
