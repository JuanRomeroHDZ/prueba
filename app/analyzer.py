import json
import pandas as pd
from database import get_connection

def load_user_profile(profile_path="my_profile.json"):
    try:
        with open(profile_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"skills": [], "certifications": []}

def analyze_skill_gap():
    profile = load_user_profile()
    my_skills = set(s.lower() for s in profile.get("skills", []))
    
    conn = get_connection()
    df = pd.read_sql_query("SELECT tecnologias FROM jobs WHERE tecnologias IS NOT NULL AND tecnologias != ''", conn)
    conn.close()
    
    if df.empty:
        return {"match_percentage": 0.0, "missing_skills": [], "top_market_skills": {}}
    
    all_skills = []
    for row in df["tecnologias"]:
        skills = [s.strip().lower() for s in row.split(",") if s.strip()]
        all_skills.extend(skills)
        
    skill_counts = pd.Series(all_skills).value_counts()
    top_market_skills = skill_counts.head(10).to_dict()
    
    # Calcular brecha sobre las habilidades más demandadas en el mercado
    matched_skills = set(top_market_skills.keys()).intersection(my_skills)
    missing_skills = list(set(top_market_skills.keys()) - my_skills)
    
    match_percentage = (len(matched_skills) / len(top_market_skills) * 100) if top_market_skills else 0.0
    
    return {
        "match_percentage": round(match_percentage, 1),
        "missing_skills": [s.capitalize() for s in missing_skills],
        "top_market_skills": {k.capitalize(): v for k, v in top_market_skills.items()}
    }
