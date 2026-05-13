from app.rag.retriever import format_contexts, retrieve_context


def main() -> None:
    query = "Tôi muốn đi Đà Lạt 1 ngày, thích cafe chill và không gian xanh"

    contexts = retrieve_context(query, limit=5)

    print("QUERY:")
    print(query)
    print("\nRESULTS:")
    print(format_contexts(contexts))


if __name__ == "__main__":
    main()