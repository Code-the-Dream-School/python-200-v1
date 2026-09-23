# Knowledge Augmentation for LLMs
Modern large language models are astonishingly good at generating fluent, human-like text. But as we learned in [Week 5](../05_AI_intro.md), they are ultimately very sophisticated autocomplete systems. They produce language that sounds right, but were not trained to generate *truth*.

This is why hallucinations happen: the model fills gaps with confident guesses, misremembers facts, or invents details that fit the conversation. Even when the model is trying to be helpful, it may prioritize what it thinks you want to hear over what is actually correct. And because LLMs are trained on data from the past, with a fixed cutoff date, they rapidly fall out of sync with current information.

When we want an LLM to behave more like a truth-tracking assistant rather than a storyteller, we need to augment its knowledge. Over the last few years, three main approaches have emerged: prompt engineering, fine-tuning, and retrieval-augmented generation (RAG). Each approach has its place, and professional AI systems often use more than one. If you want an LLM to be more accurate and up-to-date, then the tools in this week's lessons are what you will need to reach for. 

In this quick overview, we'll discuss each method, and then in the rest of the hands-on lessons for this week, we will do a much deeper dive into RAG. 

## Prompt engineering
The simplest way to give a model new information, [which we discussed last week](../05_AI_intro/prompt_engineering.md), is *prompt engineering*. In this context, it is sometimes called *prompt injection*. 

Here, you attach the required information or facts directly into the prompt: you simply tell the model what it needs to know before asking it your question. This is sometimes called "stuffing" or "in-context learning." If the information is short, stable, and changes often, this can be surprisingly effective. It is also simple and works very quickly. 

The downside is that prompts can become long and unwieldy, and the model can forget or ignore parts of them as the conversation grows. Also, these prompts consume tokens which can become costly: if you want to paste huge document stores into the prompt, then it is not cost effective. 

## Fine-tuning
A more heavyweight approach is fine-tuning. Here, we literally retrain the neural network that contains the knowledge embodied in the LLM. This is useful when you want the model to adopt a particular style or internalize patterns that are too complex to express in a prompt. The tradeoff is cost and rigidity: fine-tuning requires many examples, and can be quite costly. OpenAI has a fine-tuning API, and [it is fairly easy to use and build your own custom LLM](https://www.datacamp.com/tutorial/fine-tuning-openais-gpt-4-step-by-step-guide) using their interface, if you have training data. The main concern is cost. 

## RAG
The third approach sits between the above two in terms of complexity: retrieval-augmented generation, or RAG. Instead of trying to store new knowledge inside the model's parameters, RAG retrieves relevant information from an external knowledge store (such as a database), and then injects that information into the LLM prompt. That way, the LLM can have that information in its query. 

The way the knowledge retrieval step works can be as simple as keyword search, or it can be more sophisticated semantic search over a database. RAG systems are powerful because they combine an LLM's reasoning with a searchable database: the database can be updated on premises at any time without retraining the model. 

If your business has large corpus of information that you need to quickly access to build a more accurate LLM responses, RAG is a great avenue. 

### Where we are headed
In this week's coming lessons, partly because of their importance in industry, we will focus on RAG systems. We will start with the most brittle version, keyword-based retrieval, to highlight the basic logic of RAG. Then we move to naive semantic RAG, where chunks of text are converted to embeddings and stored in a vector database. Finally, we will move to a framework (LlamaIndex) to recreate the same idea in a more production-ready form with much less code. This is more like what you will see in industry. 

# Additional materials
There are lots of resources on the problem of hallucination in LLMs. For instance:
https://www.nngroup.com/articles/ai-hallucinations/

For more on prompt engineering, fine-tuning, and RAG, see the following:

- [Article: RAG vs fine-tuning vs prompt engineering](https://www.k2view.com/blog/rag-vs-fine-tuning-vs-prompt-engineering/#RAG-vs-fine-tuning-vs-prompt-engineering-compared)
- [Video: RAG vs fine-tuning vs Prompt engineering](https://www.youtube.com/watch?v=zYGDpG-pTho)
