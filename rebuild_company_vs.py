from vector_utils import CourseVectorStore
import os

def manual_rebuild():
    print("🔄 Starting manual vector index rebuild...")
    
    # Check if index files exist
    if os.path.exists("faiss_index.bin"):
        print("📁 Found existing faiss_index.bin - will be replaced")
    else:
        print("📁 No existing faiss_index.bin found")
        
    if os.path.exists("courses.pkl"):
        print("📁 Found existing courses.pkl - will be replaced")
    else:
        print("📁 No existing courses.pkl found")
    
    print("\n🔄 Force rebuilding vector index...")
    
    # Force rebuild by setting force_rebuild=True
    store = CourseVectorStore(force_rebuild=True)
    
    print(f"✅ Vector index rebuilt successfully!")
    print(f"📊 Total courses indexed: {len(store.courses)}")
    
    # Test the rebuilt index
    print("\n🧪 Testing rebuilt index...")
    test_results = store.semantic_query("aggiornamento", top_k=2)
    
    print("📋 Sample results with cleaned testocosto:")
    for i, course in enumerate(test_results, 1):
        title = course.get('titolo', 'No title')
        testocosto = course.get('testocosto', 'No cost info')
        print(f"  {i}. {title}")
        print(f"     Cost: {testocosto}")
    
    print("\n🎉 Manual rebuild completed successfully!")
    print("💡 You can now restart your Streamlit app to use the updated index.")

if __name__ == "__main__":
    manual_rebuild()