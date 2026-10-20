# Search Technologies – Project Gutenberg Search Engine

An information retrieval project that builds a searchable index over a collection of 10,000 Project Gutenberg books.

The project processes raw book text and metadata, removes Project Gutenberg boilerplate, performs language-aware text preprocessing, builds a Whoosh search index, and supports ranked searches across book content, titles and authors.

It also supports exact phrase searching, multilingual stemming and stop-word removal, index statistics, and generation of ranked search results in a standard submission format.

## Project Overview

The dataset consists of approximately 10,000 books from Project Gutenberg.

Each book contains metadata including:

- Gutenberg ID
- Filename
- Title
- Author
- Language
- Full book text

The project combines the metadata and corresponding text files into a single JSONL dataset before preprocessing and indexing the collection.

The main goal is to retrieve the most relevant books for a user query using a ranked information retrieval system.

## Pipeline

```text
Book metadata CSV + raw book files
                ↓
Match metadata to book text
                ↓
Remove Project Gutenberg boilerplate
                ↓
Create JSONL dataset
                ↓
Normalise and preprocess text
                ↓
Language-specific stemming + stop-word removal
                ↓
Build Whoosh index
                ↓
Search title, author and book content
                ↓
Rank results
                ↓
Output search results / submission results
```

## Data Preparation
### Match Metadata and Book Text
Book metadata is loaded from the CSV dataset and matched with the corresponding Project Gutenberg text file.

The resulting records are written to books.jsonl and contain:
- Gutenberg ID
- Filename
- Title
- Author
- Language
- Full text
The loader also handles gzip-compressed books where required.

### Remove Project Gutenberg Boilerplate
Project Gutenberg books include standard headers and footers surrounding the actual book content.

The preprocessing pipeline detects both newer and older Gutenberg markers and removes this boilerplate before indexing.

This reduces irrelevant repeated text in the searchable corpus.

### Text Normalisation
Text is normalised before indexing by:
- converting text to lowercase
- removing URLs
- removing punctuation
- normalising whitespace

Metadata such as titles and authors is normalised separately.

### Multilingual Preprocessing
The project contains language-specific preprocessing for multiple European languages:
- English
- French
- German
- Finnish
- Dutch
- Italian
- Spanish
- Portuguese
- Swedish
- Danish
NLTK stop-word lists are used to remove common words for each supported language.

Snowball stemmers are then used to reduce words to their root forms.

For languages without a configured stemmer or stop-word list, the original tokens are retained.

Stemmed words are cached to reduce repeated processing during indexing.

## Search Index
The search engine uses Whoosh to construct the index.

The schema contains the following fields:
- gutenberg_id
- title
- author
- language
- text
- text_phrase
Two versions of the book text are indexed.

### Processed Text
The text field contains language-specific processed text with stop-word removal and stemming.

This is useful for general information retrieval where related forms of a word should be treated similarly.

### Phrase Text
The text_phrase field contains normalised text without stemming.

This preserves the original word sequence and allows exact phrases to be searched more effectively.

### Ranked Search
Queries can search several parts of each book simultaneously.

The search system combines:
- Normal body-text search
- Title search
- Author search
- Exact phrase search
The results from these searches are combined into a single ranked query.

Different fields are weighted to reflect their relevance:
Search Type	Boost
Body text	1.0
Exact phrase	1.5
Title	2.5
Author	3.0

This means that, for example, a query matching a book's author receives a stronger relevance signal than the same term appearing somewhere in the body of the book.

The final results are ranked using Whoosh's relevance scoring.

### Phrase Search
Exact phrase searching is supported using the unstemmed text_phrase index.

For example:
"he has plundered our seas"

can be searched as a phrase rather than as a collection of independent terms.

This is particularly useful when searching for quotations or distinctive passages.

### Search Output
Normal searches return up to 20 ranked results.

Each result includes:
- Rank
- Gutenberg ID
- Title
- Author
- Relevance score
The results are saved as text files inside:
results/
