# Week 5: Introduction to AI
Welcome to Week 5 of Python 200! Over the past few weeks, we have built intuition for how machine learning works by using regression and classification models. Week 2 also briefly introduced neural networks, which are the models used in deep learning. This week we zoom out to look at the most consequential application of neural networks right now: large language models, or LLMs. ChatGPT, Claude, Gemini, and similar systems are all neural networks, but trained at a scale that gives them remarkable generative capabilities that have transformed how people interact with software.

As a data engineer, you will increasingly be asked to build pipelines that incorporate LLM components: chatbots, content moderation systems, document processing tools, and more. This week we focus on how to work with these models through APIs -- you don't need to train one, but you do need to understand how they work and how to use them effectively. We will also spend time on prompt engineering, the practical skill of getting reliable, useful outputs from a model. 

We will end by taking a look at some of the important ethical questions that come with deploying AI systems. Some people argue we should reconsider the use of large language models. Why? We want to create space for that perspective in this class, while also making sure you have the skills to use these tools if you do chose to use them. 

## Topics
1. [Introduction to language processing and LLMs](https://github.com/Code-the-Dream-School/python-200/blob/main/lessons/05_AI_intro/01_intro_nlp_llms.md)  
Overview of the field of natural language processing (NLP), and the recent explosion of interest in large language models (LLM). We do a fairly deep dive into how LLMs work, from tokenization to embedding, as this is the basis for so many pipelines.

2. [OpenAI Chat Completions API](https://github.com/Code-the-Dream-School/python-200/blob/main/lessons/05_AI_intro/02_completions_api.md)  
Intro and overview of the OpenAI chat completions API: this is the bread and butter of how we will interact with an LLM. We also discuss and demonstrate the moderations endpoint to filter out inappropriate content.

3. [Chatbots](https://github.com/Code-the-Dream-School/python-200/blob/main/lessons/05_AI_intro/03_chatbots.md)  
By default, LLMs have no memory of previous messages. This lesson covers how to work around that limitation to build a chatbot that can hold a coherent conversation.

4. [Prompt engineering](https://github.com/Code-the-Dream-School/python-200/blob/main/lessons/05_AI_intro/04_prompt_engineering.md)  
There are better and worse ways to get responses from a model, here we'll go over the fundamentals of *prompt engineering*. Zero shot, one shot, few-shot, and chain of thought prompting.

5. [Ethics, bias, and responsible AI](https://github.com/Code-the-Dream-School/python-200/blob/main/lessons/05_AI_intro/05_ai_and_ethics.md)    
LLMs are just ML models trained on data, so they are subject to the same biases as other models -- and they come with additional concerns around energy use, misinformation, and labor displacement. A lot of people are telling us how AI is going to change our lives for the better, but there are real ethical questions to consider in this new landscape.

