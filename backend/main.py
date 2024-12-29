# summarize the latest news from the x platform

# 1. get the latest news from the x platform
# 2. summarize the news
# 3. store the summarized news in a database
# 4. return the summarized news

from flask import Flask, request, jsonify
import requests
import sqlite3
from datetime import datetime
from typing import Dict

app = Flask(__name__)

TOPIC_DESCRIPTIONS = {
    "Technology": {
        "high": "major and minor developments, innovations, product releases, and tech trends",
        "low": "only groundbreaking news or significant shifts in the tech landscape"
    },
    "Space": {
        "high": "all space-related activities including launches, discoveries, and ongoing missions",
        "low": "significant events like successful missions or major astronomical discoveries"
    },
    "AI": {
        "high": "AI research, new AI applications, ethical debates, and policy changes",
        "low": "pivotal AI advancements or regulatory news with wide impact"
    },
    "Science": {
        "high": "broad range of scientific news from various fields",
        "low": "breakthroughs or findings that could shift scientific paradigms"
    },
    "Geopolitics": {
        "high": "international relations, policy changes, conflicts, and diplomatic events",
        "low": "events that significantly alter international power dynamics or major policy shifts"
    },
    "Business": {
        "high": "market trends, corporate news, economic developments, and industry analysis",
        "low": "major market shifts or significant corporate developments"
    },
    "Entrepreneurship": {
        "high": "startup news, funding rounds, entrepreneurial success stories, and business trends",
        "low": "most impactful entrepreneurial activities or major business news"
    },
    "Sustainability": {
        "high": "environmental initiatives, clean energy, conservation efforts, and climate action",
        "low": "major environmental breakthroughs or significant climate policy changes"
    },
    "UNSDG": {
        "high": "progress on UN Sustainable Development Goals, initiatives, and global development news",
        "low": "significant milestones or major policy changes related to SDGs"
    }
}

def normalize_weight(weight: float) -> float:
    """Convert input weight (0-10) to normalized weight (0-1)"""
    return min(max(weight / 10.0, 0.0), 1.0)

def create_prompt(topics: Dict[str, float], location: str = "India") -> str:
    """Create a detailed prompt based on topic weights and location"""
    prompt_parts = [
        f"Please summarize today's news from X on the following topics with the specified weights, "
        f"focusing on how each relates to {location}:\n\n"
    ]
    
    for topic, weight in topics.items():
        normalized_weight = normalize_weight(weight)
        if topic in TOPIC_DESCRIPTIONS:
            description = TOPIC_DESCRIPTIONS[topic]["high"] if normalized_weight > 0.7 else TOPIC_DESCRIPTIONS[topic]["low"]
            prompt_parts.append(f"{topic} (Weight: {weight}/10):\n"
                              f"- Focus on {description}")
    
    prompt_parts.append("\nPlease structure the summary in bullet points, providing more depth and "
                       "breadth for higher-weighted topics and limiting to the most critical news for "
                       "lower-weighted ones.")
    
    return "\n".join(prompt_parts)

def call_grok_api(prompt: str) -> str:
    """Make call to Grok API with the generated prompt"""
    # Replace with actual Grok API endpoint and authentication
    api_url = "https://api.grok.com/v1/summarize"
    headers = {
        "Authorization": "Bearer YOUR_GROK_API_KEY",
        "Content-Type": "application/json"
    }
    
    payload = {
        "prompt": prompt,
        "max_tokens": 1000,  # Increased for detailed bullet points
        "format": "bullet_points"
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["summary"]
    except requests.exceptions.RequestException as e:
        return str(e)

def store_summary(summary: str, topics: Dict[str, float], location: str):
    """Store the summary, topics, and location in SQLite database"""
    conn = sqlite3.connect('summaries.db')
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS summaries
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         summary TEXT NOT NULL,
         location TEXT NOT NULL,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS topics
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         summary_id INTEGER,
         topic TEXT NOT NULL,
         weight FLOAT NOT NULL,
         FOREIGN KEY(summary_id) REFERENCES summaries(id))
    ''')
    
    # Store summary
    cursor.execute('INSERT INTO summaries (summary, location) VALUES (?, ?)', 
                  (summary, location))
    summary_id = cursor.lastrowid
    
    # Store topics
    for topic, weight in topics.items():
        cursor.execute('INSERT INTO topics (summary_id, topic, weight) VALUES (?, ?, ?)',
                      (summary_id, topic, normalize_weight(weight)))
    
    conn.commit()
    conn.close()

@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        data = request.get_json()
        if not isinstance(data, dict) or 'topics' not in data:
            return jsonify({
                "error": "Request body must include 'topics' object with topic-weight pairs"
            }), 400
        
        location = data.get('location', 'India')
        topics = data['topics']
        
        # Validate topics and weights
        for topic, weight in topics.items():
            if not isinstance(weight, (int, float)) or weight < 0 or weight > 10:
                return jsonify({
                    "error": f"Weight for topic '{topic}' must be a number between 0 and 10"
                }), 400
        
        # Generate prompt based on topics and weights
        prompt = create_prompt(topics, location)
        
        # Get summary from Grok API
        summary = call_grok_api(prompt)
        
        # Store in database
        store_summary(summary, topics, location)
        
        return jsonify({
            "summary": summary,
            "timestamp": datetime.now().isoformat(),
            "location": location,
            "topics": {topic: float(weight) for topic, weight in topics.items()}
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)



