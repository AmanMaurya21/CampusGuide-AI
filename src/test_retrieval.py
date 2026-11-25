
from src.vector_store import search_documents


def main():
    queries = [
        "What is the attendance policy?",
        "How can I borrow books from the library?",
        "What are the placement opportunities?",
        "How can students connect to campus Wi-Fi?",
        "What scholarships are available for students?",
    ]

    for query in queries:
        print("\n" + "=" * 70)
        print(f"QUERY: {query}")
        print("=" * 70)

        results = search_documents(query, top_k=3)

        for result in results:
            print(f"\nResult {result['rank']}")
            print(f"Source: {result['source']}")
            print(f"Distance: {result['distance']:.4f}")
            print("Content:")
            print(result["content"][:1000])


if __name__ == "__main__":
    main()
