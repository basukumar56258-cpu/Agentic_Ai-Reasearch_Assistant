import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from tavily import TavilyClient

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def configured_secret(value):
    if not value:
        return False
    lowered = value.lower()
    return len(value) > 10 and not any(
        marker in lowered for marker in ("your_", "placeholder", "replace", "example")
    )

def get_clients():
    openai_key = os.getenv("OPENAI_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    if not configured_secret(openai_key):
        raise RuntimeError("OPENAI_API_KEY is missing in backend/.env")
    if not configured_secret(tavily_key):
        raise RuntimeError("TAVILY_API_KEY is missing in backend/.env")
    return OpenAI(api_key=openai_key), TavilyClient(api_key=tavily_key)

def planner(client, query):
    prompt = f"""
You are a research planning agent.
Break the user request into 3 focused web-search subquestions.
Return ONLY valid JSON:
{{"subquestions":["...", "...", "..."]}}

User request:
{query}
"""
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.2,
        messages=[{"role": "user", "content": prompt}],
    )
    return json.loads(response.choices[0].message.content)["subquestions"][:3]

def web_research(tavily, subquestions):
    sources = []
    for question in subquestions:
        result = tavily.search(
            query=question,
            search_depth="advanced",
            max_results=5,
            include_answer=False,
        )
        for item in result.get("results", []):
            sources.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "content": item.get("content", ""),
            })

    unique = {}
    for source in sources:
        if source["url"]:
            unique[source["url"]] = source
    return list(unique.values())[:12]

def synthesizer(client, query, sources):
    evidence = "\n\n".join(
        f"TITLE: {s['title']}\nURL: {s['url']}\nCONTENT: {s['content'][:4000]}"
        for s in sources
    )
    prompt = f"""
You are the synthesis agent in an Agentic AI Research Assistant.

Research question:
{query}

Use ONLY the supplied research evidence. Do not invent facts.
Write:
1. Executive Summary
2. Key Findings
3. Important Details
4. Limitations / Uncertainty
5. Conclusion

Use inline source markers [1], [2], etc. matching the source list.
If evidence conflicts, explicitly mention the conflict.

Research evidence:
{evidence}
"""
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.2,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

def research(query):
    client, tavily = get_clients()
    subquestions = planner(client, query)
    sources = web_research(tavily, subquestions)

    if not sources:
        raise RuntimeError("No web research results were found.")

    report = synthesizer(client, query, sources)

    return {
        "query": query,
        "plan": subquestions,
        "report": report,
        "sources": [
            {"id": i + 1, "title": s["title"], "url": s["url"]}
            for i, s in enumerate(sources)
        ],
    }
