from whoosh import index

def get_index_statistics():

    ix = index.open_dir("indexed_text")

    with ix.searcher() as searcher:
        print(f"Weighting model: {searcher.weighting}\nWeighting type: {type(searcher.weighting)} \n")

    with ix.reader() as reader:
        fields = ["text", "text_phrase"]

        print(f"Documents indexed: {reader.doc_count_all()}\n")

        for field in fields:
            vocabulary_size = 0
            total_postings = 0

            for term in reader.field_terms(field):
                vocabulary_size += 1
                total_postings += reader.doc_frequency(field, term)

            total_tokens = reader.field_length(field)

            print(f"Field: {field}")
            print(f"Vocabulary size: {vocabulary_size}")
            print(f"Total tokens: {total_tokens}")
            print(f"Total postings: {total_postings}\n")