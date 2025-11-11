import json
import os
import random
from datetime import datetime, timedelta

# Define the base path relative to this file's location
BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

# --- Data Pools for Realistic Profiles ---
EXAM_AREAS = {
    "Fiscal": {
        "exams": ["Receita Federal - Auditor", "SEFAZ-SP - Agente Fiscal", "ISS-RJ - Fiscal de Rendas"],
        "subjects": ["Direito Tributário", "Contabilidade Geral", "Auditoria", "Legislação Aduaneira", "Comércio Internacional"]
    },
    "Tribunais": {
        "exams": ["TJ-SP - Escrevente", "TRF-2 - Técnico Judiciário", "TRT-1 - Analista Judiciário"],
        "subjects": ["Direito Constitucional", "Direito Administrativo", "Português", "Raciocínio Lógico", "Normas da Corregedoria"]
    },
    "Policial": {
        "exams": ["Polícia Federal - Agente", "PRF - Policial Rodoviário", "PC-RJ - Inspetor"],
        "subjects": ["Direito Penal", "Direito Processual Penal", "Legislação Especial", "Contabilidade", "Informática"]
    }
}

USER_NAMES = ["ana", "bruno", "carla", "daniel", "elisa", "felipe"]

def generate_random_profile(profile_name: str) -> dict:
    """Generates a more realistic random user profile dictionary."""
    user_name = profile_name
    study_level = random.choice(["Iniciante", "Intermediário", "Avançado"])

    # Select an area and then an exam and subjects from that area
    area_name = random.choice(list(EXAM_AREAS.keys()))
    exam_name = random.choice(EXAM_AREAS[area_name]["exams"])
    
    cycle_name = f"Ciclo {random.choice(['Intensivo', 'Pós-Edital', 'Regular'])} - {datetime.now().year}"
    is_active = True
    daily_goal_blocks = random.randint(2, 5)

    # Select a subset of subjects for the cycle
    available_subjects = EXAM_AREAS[area_name]["subjects"]
    num_subjects = random.randint(3, min(5, len(available_subjects)))
    selected_subjects_names = random.sample(available_subjects, num_subjects)

    subjects = []
    for subject_name in selected_subjects_names:
        subjects.append({
            "name": subject_name,
            "relevance_weight": random.randint(3, 5),
            "volume_weight": random.randint(2, 5),
            "difficulty_weight": random.randint(2, 4),
            "current_strategic_state": random.choice(["MAINTAIN", "DEEP_WORK", "DISCOVERY", "CONQUER", "CEMENT"])
        })

    sessions = []
    num_sessions = random.randint(5, 15) # More sessions for better data
    for _ in range(num_sessions):
        subject = random.choice(subjects)
        # Sessions spread over the last 60 days
        start_time = (datetime.now() - timedelta(days=random.randint(0, 60), hours=random.randint(0, 23))).isoformat(timespec='seconds') + 'Z'
        liquid_duration_sec = random.randint(2400, 7200) # 40 mins to 2 hours

        questions = []
        num_questions = random.randint(0, 30)
        for _ in range(num_questions):
            questions.append({
                "topic_name": f"tópico_{random.randint(1, 5)}", # Generic topics for now
                "is_correct": random.choice([True, True, False]) # 2/3 chance of being correct
            })
        sessions.append({
            "subject_name": subject["name"],
            "start_time": start_time,
            "liquid_duration_sec": liquid_duration_sec,
            "questions": questions
        })

    profile = {
        "user": {
            "name": user_name,
            "study_level": study_level
        },
        "exam": {
            "name": exam_name,
            "area": area_name
        },
        "cycle": {
            "name": cycle_name,
            "is_active": is_active,
            "daily_goal_blocks": daily_goal_blocks,
            "subjects": subjects,
            "sessions": sessions
        }
    }
    return profile

if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Generate random user profile JSON files.")
    parser.add_argument("--count", type=int, default=1, help="Number of profiles to generate.")
    parser.add_argument("--output-dir", type=str, default=os.path.join(BASE_PATH, "tests", "fixtures", "profiles"),
                        help="Directory to save the generated profiles.")

    args = parser.parse_args()

    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)

    for i in range(args.count):
        profile_name = f"{random.choice(USER_NAMES)}_{i+1}"
        profile_data = generate_random_profile(profile_name)
        file_path = os.path.join(output_dir, f"{profile_name}.json")
        with open(file_path, "w", encoding='utf-8') as f:
            json.dump(profile_data, f, indent=2, ensure_ascii=False)
        print(f"Generated profile: {file_path}")

    print(f"Generated {args.count} random profiles in {output_dir}")