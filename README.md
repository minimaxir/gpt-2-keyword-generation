# gpt-2-keyword-generation

A method for encoding a dataset of text documents into a form that when finetuned with GPT-2, the network will be able to generate text pertaining to the specified keywords.

## Simple Usage

This repo contains a script which attempts to extract the keywords in an unsupervised manner (although you can provide your own keywords if you have them). The methodology is as follows for each text document:

1. Extract the noun chunks from each document as "keywords" using spaCy.
	* The spaCy parser does a good job of capturing compound nouns and full proper nouns (e.g. "elon-musk" instead of "elon" and "musk")
2. Prepare the keywords in such a way that the document text is generated conditionally on the keywords.
	* Normalize the keywords (make lower case, replace spaces/punctuation w/ dashes) and dedupe the keywords in a given document.
	* When processing the keywords, skip each keyword according to the `dropout` rate (default: 0.5) to prevent GPT-2 for memorizing that the presence of a keyword (or lack thereof) can determine the text.
	* Shuffle the order of the keywords to prevent GPT-2 from cheating and learning when the order of the keywords should be written in the document proper.
	* For each set of keywords in a document, create `repeat` random combinations (default: 3) of the keywords
	* The max number of keywords is capped at `max_keywords` (default: 3) to prevent overfitting, but in combination with `dropout` and `repeat`, still gives more keyword group possibilities than just 3 from a document to be present.
3. Write the keywords, then the document for each generated set of keywords.

## Advanced Usage

This script is also capable of handling additional hierarchal conditions. This script has 4 total possibilities implemented:
`category`, `keywords`, `title`, and `body`. In this case

## Helpful Notes

* The scope of the text document plus the keywords must be within gpt-2's max scope (e.g. should only be a paragraph or two max).
* Manual tagging may work better, and that is an option.

## Maintainer/Creator

Max Woolf ([@minimaxir](https://minimaxir.com))

*Max's open-source projects are supported by his [Patreon](https://www.patreon.com/minimaxir). If you found this project helpful, any monetary contributions to the Patreon are appreciated and will be put to good creative use.*

## License

MIT

## Disclaimer

This repo has no affiliation or relationship with OpenAI.