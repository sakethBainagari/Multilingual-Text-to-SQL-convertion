"""
Test if sentence-transformers works properly
"""
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # Suppress TensorFlow warnings

try:
    print("Testing FAISS...")
    import faiss
    print(f"✅ FAISS working! Version: {faiss.__version__}")
    
    print("\nTesting sentence-transformers...")
    from sentence_transformers import SentenceTransformer
    print("✅ sentence-transformers import successful!")
    
    print("\nLoading embedding model (this may take a moment)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("✅ Model loaded successfully!")
    
    print("\nTesting embedding generation...")
    test_sentence = "This is a test query"
    embedding = model.encode(test_sentence)
    print(f"✅ Generated embedding with shape: {embedding.shape}")
    print(f"   Embedding dimension: {len(embedding)}")
    
    print("\n" + "="*50)
    print("✅ ALL TESTS PASSED!")
    print("✅ Vector database is ready to use!")
    print("="*50)
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("\nTrying alternative approach...")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
