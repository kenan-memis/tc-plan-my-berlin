# Hard #9 — RAGAs evaluation summary (hard9-smoke2)

- Judge model: `gpt-4o-mini`
- TripProfile model/provider: `gpt-4o-mini` / `openai`
- Samples: `2`
- top_k_contexts: `6`

## Raw results

### Metric averages

- faithfulness: 0.1250
- answer_relevancy: 0.8856
- context_precision: 0.5000
- context_recall: 0.6333

### Per-sample table

```json
[
  {
    "user_input": "What are some famous sights in Mitte?",
    "retrieved_contexts": [
      "## Mitte\n\n### Brandenburg Gate\n- Type: Landmark\n- Neighbourhood: Mitte\n- Tags: history, iconic, outdoor\n- Typical visit time: 30–60 minutes\n- Summary: One of Berlin’s most famous landmarks and a symbol of German reunification. Built in the 18th century, it once stood between East and West Berlin during the Cold War. Best visited early morning or late evening to avoid crowds.\n\n### Museum Island\n- Type: Museum cluster\n- Neighbourhood: Mitte\n- Tags: museums, culture, indoor\n- Typical visit time: 3–5 hours\n- Summary: A UNESCO World Heritage site featuring five major museums, including the Pergamon Museum and Neues Museum. Ideal for art and history lovers; plan ahead as visiting all museums takes several hours.",
      "## Mitte\n\n### Brandenburg Gate\n- Type: Landmark\n- Neighbourhood: Mitte\n- Tags: history, iconic, outdoor\n- Typical visit time: 30–60 minutes\n- Summary: One of Berlin’s most famous landmarks and a symbol of German reunification. Built in the 18th century, it once stood between East and West Berlin during the Cold War. Best visited early morning or late evening to avoid crowds.\n\n### Museum Island\n- Type: Museum cluster\n- Neighbourhood: Mitte\n- Tags: museums, culture, indoor\n- Typical visit time: 3–5 hours\n- Summary: A UNESCO World Heritage site featuring five major museums, including the Pergamon Museum and Neues Museum. Ideal for art and history lovers; plan ahead as visiting all museums takes several hours.",
      "# Berlin – Places and Neighbourhoods",
      "# Berlin – Places and Neighbourhoods",
      "## Mitte\n\n### Monsieur Vuong\n- Type: Sit-down\n- Neighbourhood: Mitte\n- Cuisine: Vietnamese\n- Price level: $$\n- Tags: casual, popular, quick\n- Summary: A well-known Vietnamese restaurant with fresh, flavorful dishes. Often busy, but service is fast and efficient.\n\n### Zur letzten Instanz\n- Type: Sit-down\n- Neighbourhood: Mitte\n- Cuisine: German\n- Price level: $$\n- Tags: traditional, historic, cosy\n- Summary: Berlin’s oldest restaurant, serving classic German dishes in a historic setting. Great for experiencing traditional cuisine.\n\n### House of Small Wonder\n- Type: Café / brunch\n- Neighbourhood: Mitte\n- Cuisine: International\n- Price level: $$\n- Tags: brunch, trendy, cosy\n- Summary: A stylish café known for its brunch menu and unique interior design. Popular with both locals and tourists.",
      "## Mitte\n\n### Monsieur Vuong\n- Type: Sit-down\n- Neighbourhood: Mitte\n- Cuisine: Vietnamese\n- Price level: $$\n- Tags: casual, popular, quick\n- Summary: A well-known Vietnamese restaurant with fresh, flavorful dishes. Often busy, but service is fast and efficient.\n\n### Zur letzten Instanz\n- Type: Sit-down\n- Neighbourhood: Mitte\n- Cuisine: German\n- Price level: $$\n- Tags: traditional, historic, cosy\n- Summary: Berlin’s oldest restaurant, serving classic German dishes in a historic setting. Great for experiencing traditional cuisine.\n\n### House of Small Wonder\n- Type: Café / brunch\n- Neighbourhood: Mitte\n- Cuisine: International\n- Price level: $$\n- Tags: brunch, trendy, cosy\n- Summary: A stylish café known for its brunch menu and unique interior design. Popular with both locals and tourists."
    ],
    "response": "Brandenburg Gate (Mitte)\nMonsieur Vuong (Mitte)\nMonsieur Vuong (Mitte)\nCurry 61 (Mitte)\nGörlitzer Park (Kreuzberg)",
    "reference": "Brandenburg Gate (Mitte)\nMonsieur Vuong (Mitte)\nMonsieur Vuong (Mitte)\nCurry 61 (Mitte)\nGörlitzer Park (Kreuzberg)",
    "faithfulness": 0.25,
    "answer_relevancy": 0.8998156261239092,
    "context_precision": 0.99999999995,
    "context_recall": 0.6
  },
  {
    "user_input": "Recommend 2 restaurants in Kreuzberg with low budget.",
    "retrieved_contexts": [
      "## Kreuzberg\n\n### Görlitzer Park\n- Type: Park\n- Neighbourhood: Kreuzberg\n- Tags: outdoor, local, relaxed\n- Typical visit time: 1–2 hours\n- Summary: A popular park among locals, especially in summer. Known for its laid-back atmosphere, street food vendors, and multicultural vibe.\n\n### Markthalle Neun\n- Type: Food market\n- Neighbourhood: Kreuzberg\n- Tags: food, indoor, local\n- Typical visit time: 1–2 hours\n- Summary: A historic market hall offering local and international food. Street Food Thursday is especially popular, with many small vendors and a lively atmosphere.",
      "## Kreuzberg\n\n### Görlitzer Park\n- Type: Park\n- Neighbourhood: Kreuzberg\n- Tags: outdoor, local, relaxed\n- Typical visit time: 1–2 hours\n- Summary: A popular park among locals, especially in summer. Known for its laid-back atmosphere, street food vendors, and multicultural vibe.\n\n### Markthalle Neun\n- Type: Food market\n- Neighbourhood: Kreuzberg\n- Tags: food, indoor, local\n- Typical visit time: 1–2 hours\n- Summary: A historic market hall offering local and international food. Street Food Thursday is especially popular, with many small vendors and a lively atmosphere.",
      "# Berlin – Places and Neighbourhoods",
      "# Berlin – Places and Neighbourhoods",
      "### Kulturbrauerei\n- Type: Cultural complex\n- Neighbourhood: Prenzlauer Berg\n- Tags: culture, nightlife, history\n- Typical visit time: 2–3 hours\n- Summary: A former brewery turned into a cultural hub with museums, cinemas, and event spaces. Hosts exhibitions and nightlife events throughout the year.\n\n---",
      "### Kulturbrauerei\n- Type: Cultural complex\n- Neighbourhood: Prenzlauer Berg\n- Tags: culture, nightlife, history\n- Typical visit time: 2–3 hours\n- Summary: A former brewery turned into a cultural hub with museums, cinemas, and event spaces. Hosts exhibitions and nightlife events throughout the year.\n\n---"
    ],
    "response": "Görlitzer Park (Kreuzberg)\nMustafa’s Gemüse Kebap (Kreuzberg)\nGörlitzer Park (Kreuzberg)",
    "reference": "Görlitzer Park (Kreuzberg)\nMustafa’s Gemüse Kebap (Kreuzberg)\nGörlitzer Park (Kreuzberg)",
    "faithfulness": 0.0,
    "answer_relevancy": 0.8714032494649577,
    "context_precision": 0.0,
    "context_recall": 0.6666666666666666
  }
]
```\n