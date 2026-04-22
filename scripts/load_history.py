#!/usr/bin/env python3
"""
Load learning history from the user-specified directory with Socratic format.

This script:
1. Reads progress.json with detailed learning trajectory
2. Reads feedback.md with user input
3. Analyzes user's learning progress and understanding level
4. Prepares context for continuing the learning journey
5. Provides learning recommendations based on feedback
"""

import os
import json
import argparse


def load_progress(base_path, topic):
    """Load learning progress from progress.json."""
    topic_dir = os.path.join(base_path, "bloom-mentor", topic)
    progress_file = os.path.join(topic_dir, "progress.json")
    
    if not os.path.exists(progress_file):
        print(f"No progress file found for topic: {topic}")
        return None
    
    with open(progress_file, 'r', encoding='utf-8') as f:
        progress = json.load(f)
    
    print(f"Loaded progress for topic: {topic}")
    return progress


def load_feedback(topic_dir):
    """Load user feedback from feedback.md."""
    feedback_file = os.path.join(topic_dir, "feedback.md")
    
    if not os.path.exists(feedback_file):
        print("No feedback file found")
        return None
    
    with open(feedback_file, 'r', encoding='utf-8') as f:
        feedback_content = f.read()
    
    print("Loaded user feedback")
    return feedback_content


def load_session_history(topic_dir):
    """Load session history from numbered article files."""
    articles = []
    
    for filename in os.listdir(topic_dir):
        if filename.endswith(".md") and filename[0:2].isdigit():
            article_path = os.path.join(topic_dir, filename)
            with open(article_path, 'r', encoding='utf-8') as f:
                content = f.read()
            articles.append({
                "filename": filename,
                "content": content
            })
    
    # Sort articles by number
    articles.sort(key=lambda x: x["filename"])
    
    print(f"Loaded {len(articles)} previous sessions")
    return articles


def analyze_learning_progress(progress):
    """Analyze user's learning progress and understanding level."""
    if not progress:
        return {
            "current_level": 1,
            "mastery_achieved": 0,
            "learning_speed": 0,
            "strengths": [],
            "weaknesses": []
        }
    
    # Calculate mastery achieved
    mastery_achieved = sum(1 for level in progress.get("mastery", {}).values() if level.get("achieved", False))
    
    # Analyze learning trajectory
    trajectory = progress.get("learning_trajectory", [])
    learning_speed = len(trajectory) / 7 if trajectory else 0  # Sessions per week
    
    # Identify strengths and weaknesses
    strengths = []
    weaknesses = []
    
    for level_key, level_info in progress.get("mastery", {}).items():
        if level_info.get("achieved", False):
            strengths.append(f"Level {level_key}")
        else:
            weaknesses.append(f"Level {level_key}")
    
    return {
        "current_level": progress.get("current_level", 1),
        "mastery_achieved": mastery_achieved,
        "learning_speed": learning_speed,
        "strengths": strengths,
        "weaknesses": weaknesses
    }


def analyze_feedback(feedback_content):
    """Analyze user feedback to identify patterns."""
    if not feedback_content:
        return {
            "questions": [],
            "confusions": [],
            "interests": [],
            "examples": []
        }
    
    # Simple parsing of feedback sections
    lines = feedback_content.split('\n')
    questions = []
    confusions = []
    interests = []
    examples = []
    
    current_section = None
    for line in lines:
        line = line.strip()
        if "我理解了" in line:
            current_section = "understanding"
        elif "我困惑的" in line:
            current_section = "confusion"
        elif "我想探索的" in line:
            current_section = "interest"
        elif "我的例子" in line:
            current_section = "example"
        elif line and current_section:
            if current_section == "confusion" and line:
                confusions.append(line)
            elif current_section == "interest" and line:
                interests.append(line)
            elif current_section == "example" and line:
                examples.append(line)
    
    return {
        "questions": [],  # Extract questions from content
        "confusions": confusions,
        "interests": interests,
        "examples": examples
    }


def generate_recommendations(progress, feedback_analysis):
    """Generate learning recommendations based on progress and feedback."""
    recommendations = []
    
    if not progress:
        return ["Start with the basics and build foundational knowledge"]
    
    # Based on current level
    current_level = progress.get("current_level", 1)
    
    # Based on feedback confusions
    if feedback_analysis.get("confusions"):
        recommendations.append("Focus on clarifying confusing concepts before advancing")
    
    # Based on interests
    if feedback_analysis.get("interests"):
        recommendations.append("Explore topics that interest you to maintain motivation")
    
    # Based on mastery
    mastery_achieved = sum(1 for level in progress.get("mastery", {}).values() if level.get("achieved", False))
    if mastery_achieved < 3:
        recommendations.append("Focus on building strong foundational knowledge")
    elif mastery_achieved < 5:
        recommendations.append("Develop critical thinking and analytical skills")
    else:
        recommendations.append("Focus on creative applications and synthesis")
    
    # Based on learning speed
    trajectory = progress.get("learning_trajectory", [])
    if len(trajectory) < 3:
        recommendations.append("Consider more frequent practice sessions")
    
    return recommendations


def prepare_learning_context(base_path, topic):
    """Prepare context for continuing the learning journey."""
    topic_dir = os.path.join(base_path, "bloom-mentor", topic)
    
    # Load progress
    progress = load_progress(base_path, topic)
    
    # Load feedback
    feedback = load_feedback(topic_dir)
    feedback_analysis = analyze_feedback(feedback)
    
    # Load session history
    sessions = load_session_history(topic_dir)
    
    # Analyze learning progress
    progress_analysis = analyze_learning_progress(progress)
    
    # Generate recommendations
    recommendations = generate_recommendations(progress, feedback_analysis)
    
    # Prepare context
    context = {
        "has_history": bool(progress),
        "message": "Found previous learning history. " + 
                  (f"Last session: {progress.get('learning_trajectory', [-1])[-1].get('date')}" if progress and progress.get('learning_trajectory') else "Ready to start learning"),
        "current_level": progress.get("current_level", 1) if progress else 1,
        "current_article": progress.get("current_article", 0) if progress else 0,
        "mastery_achieved": progress_analysis.get("mastery_achieved", 0),
        "strengths": progress_analysis.get("strengths", []),
        "weaknesses": progress_analysis.get("weaknesses", []),
        "confusions": feedback_analysis.get("confusions", []),
        "interests": feedback_analysis.get("interests", []),
        "recommendations": recommendations,
        "sessions": len(sessions),
        "last_session_date": progress.get('learning_trajectory', [-1])[-1].get('date') if progress and progress.get('learning_trajectory') else None,
        "next_steps": generate_next_steps(progress, feedback_analysis)
    }
    
    return context


def generate_next_steps(progress, feedback_analysis):
    """Generate specific next steps based on progress and feedback."""
    next_steps = []
    
    if not progress:
        return ["Start with the first learning article", "Complete the feedback section after reading"]
    
    current_level = progress.get("current_level", 1)
    
    # Based on current level
    level_actions = {
        1: "Focus on memorizing key definitions and concepts",
        2: "Practice explaining concepts in your own words",
        3: "Apply concepts to real-world scenarios",
        4: "Analyze relationships between different concepts",
        5: "Evaluate different approaches and solutions",
        6: "Create original applications of the concepts"
    }
    
    next_steps.append(level_actions.get(current_level, "Continue learning at your current level"))
    
    # Based on feedback
    if feedback_analysis.get("confusions"):
        next_steps.append("Clarify confusing concepts before moving forward")
    
    if feedback_analysis.get("interests"):
        next_steps.append("Explore topics that interest you")
    
    # Always include feedback
    next_steps.append("Provide detailed feedback after each session")
    
    return next_steps


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Load learning history with Socratic format")
    parser.add_argument("--base-path", required=True, help="Base directory for storing learning progress")
    parser.add_argument("--topic", required=True, help="Learning topic")
    
    args = parser.parse_args()
    
    # Prepare learning context
    context = prepare_learning_context(args.base_path, args.topic)
    
    # Print context
    print("\nLearning Context:")
    print("{")
    for key, value in context.items():
        if isinstance(value, list):
            print(f"  \"{key}\": [")
            for item in value:
                print(f"    \"{item}\",")
            print("  ],")
        else:
            print(f"  \"{key}\": \"{value}\",")
    print("}")
    
    # Print recommendations
    if context.get("recommendations"):
        print("\nRecommendations:")
        for i, recommendation in enumerate(context["recommendations"], 1):
            print(f"{i}. {recommendation}")
    
    # Print next steps
    if context.get("next_steps"):
        print("\nNext Steps:")
        for i, step in enumerate(context["next_steps"], 1):
            print(f"{i}. {step}")


if __name__ == "__main__":
    main()
