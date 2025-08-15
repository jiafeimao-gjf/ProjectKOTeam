from langchain_community.llms import Ollama

if __name__ == '__main__':

    llm = Ollama(model="gemma2:2b")
    for chunk in llm.stream("Why is the sky blue?"):
        print(chunk)
