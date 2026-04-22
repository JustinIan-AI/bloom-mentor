#!/usr/bin/env python3
"""
Save learning progress to the user-specified directory with Socratic format.

This script:
1. Creates the directory structure with numbered articles
2. Saves learning articles in sequential order
3. Updates progress.json with detailed learning trajectory
4. Generates feedback.md for user input
5. Creates an adaptive learning dashboard
"""

import os
import json
import argparse
from datetime import datetime


def create_directory_structure(base_path, topic):
    """Create the directory structure for storing learning progress."""
    bloom_dir = os.path.join(base_path, "bloom-mentor")
    topic_dir = os.path.join(bloom_dir, topic)
    
    # Create directories if they don't exist
    for directory in [bloom_dir, topic_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
    
    return topic_dir


def get_next_article_number(topic_dir):
    """Get the next article number based on existing files."""
    articles = []
    for filename in os.listdir(topic_dir):
        if filename.endswith(".md") and filename[0:2].isdigit():
            try:
                number = int(filename[0:2])
                articles.append(number)
            except ValueError:
                pass
    
    if not articles:
        return 1
    return max(articles) + 1


def create_learning_article(topic_dir, article_number, session_data):
    """Create a learning article with Socratic questions."""
    article_number_str = f"{article_number:02d}"
    
    # Determine article title based on Bloom level
    level_titles = {
        1: "introduction",
        2: "concepts",
        3: "application",
        4: "analysis",
        5: "evaluation",
        6: "creation"
    }
    
    current_level = session_data.get('current_level', 1)
    title_slug = level_titles.get(current_level, "learning")
    article_file = os.path.join(topic_dir, f"{article_number_str}-{title_slug}.md")
    
    # Create article content
    content = f"# {session_data['topic']}: {level_titles.get(current_level, 'Learning')}\n\n"
    
    # Add Socratic questions based on Bloom level
    content += "## Socratic Questions\n\n"
    
    if 'questions' in session_data:
        for i, question in enumerate(session_data['questions'], 1):
            content += f"{i}. {question}\n\n"
    else:
        # Generate default questions based on level
        level_questions = {
            1: ["What is the definition of the core concept?", "Can you list the key components?", "What are the basic principles?"],
            2: ["Can you explain this concept in your own words?", "How would you describe this to someone new?", "What examples illustrate this concept?"],
            3: ["How would you use this concept in a real scenario?", "What steps would you take to implement this?", "How does this solve a specific problem?"],
            4: ["What are the core differences between this and similar concepts?", "How do the components relate to each other?", "What factors influence this concept?"],
            5: ["How effective is this approach for your goal?", "What criteria would you use to assess this?", "How does this compare to alternatives?"],
            6: ["How would you design a solution using this concept?", "What new approach could solve a related problem?", "How would you integrate these ideas into a framework?"]
        }
        
        questions = level_questions.get(current_level, level_questions[1])
        for i, question in enumerate(questions, 1):
            content += f"{i}. {question}\n\n"
    
    # Add learning content
    if 'content' in session_data:
        content += "## Learning Content\n\n"
        content += session_data['content']
        content += "\n\n"
    
    # Add feedback section
    content += "---\n\n"
    content += "## 💭 学习反馈区\n\n"
    content += "读完这篇后，你可以写下：\n\n"
    content += "- **我理解了**：（用你自己的话总结核心观点）\n"
    content += "- **我困惑的**：（哪个概念或环节还不清楚）\n"
    content += "- **我想探索的**：（有没有特别想深入了解的方向）\n"
    content += "- **我的例子**：（结合你的工作/生活，举一个相关例子）\n\n"
    content += "你的反馈会帮助我调整下一篇的内容深度和方向。\n"
    
    # Write the article file
    with open(article_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Created learning article: {article_file}")
    return article_file


def create_feedback_file(topic_dir):
    """Create feedback.md file for user input."""
    feedback_file = os.path.join(topic_dir, "feedback.md")
    
    # Create feedback file if it doesn't exist
    if not os.path.exists(feedback_file):
        content = "# 学习反馈\n\n"
        content += "## 文章反馈\n\n"
        content += "在这里记录你对每篇文章的反馈：\n\n"
        
        with open(feedback_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Created feedback file: {feedback_file}")
    
    return feedback_file


def update_progress_json(topic_dir, session_data, article_number):
    """Update the progress.json file with detailed learning trajectory."""
    progress_file = os.path.join(topic_dir, "progress.json")
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # Read existing progress if it exists
    if os.path.exists(progress_file):
        with open(progress_file, 'r', encoding='utf-8') as f:
            progress = json.load(f)
    else:
        # Initialize progress structure
        progress = {
            "topic": session_data['topic'],
            "current_level": session_data['current_level'],
            "current_article": article_number,
            "mastery": {
                "1": {"achieved": False, "date": None, "evidence": []},
                "2": {"achieved": False, "date": None, "evidence": []},
                "3": {"achieved": False, "date": None, "evidence": []},
                "4": {"achieved": False, "date": None, "evidence": []},
                "5": {"achieved": False, "date": None, "evidence": []},
                "6": {"achieved": False, "date": None, "evidence": []}
            },
            "learning_trajectory": [],
            "feedback_history": [],
            "recommendations": []
        }
    
    # Update current level and article
    progress["current_level"] = session_data['current_level']
    progress["current_article"] = article_number
    
    # Record mastery if achieved
    if session_data.get('mastery_achieved', False):
        level_key = str(session_data['current_level'])
        progress["mastery"][level_key]["achieved"] = True
        progress["mastery"][level_key]["date"] = date_str
        progress["mastery"][level_key]["evidence"].extend(session_data.get('key_insights', []))
    
    # Add learning trajectory entry
    trajectory_entry = {
        "date": date_str,
        "level": session_data['current_level'],
        "article": article_number,
        "activity": session_data.get('activity', "Learning session"),
        "key_insights": session_data.get('key_insights', []),
        "areas_for_improvement": session_data.get('areas_for_improvement', []),
        "mastery_status": "Achieved" if session_data.get('mastery_achieved', False) else "In Progress"
    }
    progress["learning_trajectory"].append(trajectory_entry)
    
    # Add recommendations
    if 'next_level' in session_data:
        recommendation = {
            "date": date_str,
            "current_level": session_data['current_level'],
            "next_level": session_data.get('next_level', session_data['current_level']),
            "focus": session_data.get('session_plan', "Continue learning"),
            "preparation": session_data.get('preparation_needed', "Review current concepts")
        }
        progress["recommendations"].append(recommendation)
    
    # Write updated progress
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)
    
    print(f"Updated progress file: {progress_file}")
    return progress


def generate_index_file(base_path, topic, progress):
    """Generate the index.md dashboard file."""
    bloom_dir = os.path.join(base_path, "bloom-mentor")
    index_file = os.path.join(bloom_dir, "index.md")
    
    # Create index content
    content = f"# Bloom Socratic Learning Dashboard\n\n"
    
    # Add topic summary
    content += f"## {topic}\n\n"
    
    # Learning progress
    content += "### Learning Progress\n\n"
    content += "| Bloom Level | Status | Mastery Date | Evidence |\n"
    content += "|-------------|--------|--------------|----------|\n"
    
    level_names = {
        "1": "Remember",
        "2": "Understand",
        "3": "Apply",
        "4": "Analyze",
        "5": "Evaluate",
        "6": "Create"
    }
    
    for level_key in ["1", "2", "3", "4", "5", "6"]:
        level_info = progress["mastery"][level_key]
        status = "✅ Achieved" if level_info["achieved"] else "⏳ In Progress" if level_key == str(progress["current_level"]) else "❌ Not Started"
        date = level_info["date"] or "-"
        evidence = ", ".join(level_info["evidence"])[:100] + "..." if level_info["evidence"] else "-"
        
        content += f"| {level_names[level_key]} | {status} | {date} | {evidence} |\n"
    
    # Article history
    content += "\n### Article History\n\n"
    
    # Find all articles
    topic_dir = os.path.join(bloom_dir, topic)
    articles = []
    for filename in os.listdir(topic_dir):
        if filename.endswith(".md") and filename[0:2].isdigit():
            articles.append(filename)
    
    articles.sort()
    for article in articles:
        article_path = os.path.join(topic_dir, article)
        with open(article_path, 'r', encoding='utf-8') as f:
            title = f.readline().strip('# \n')
        content += f"- [{title}]({topic}/{article})\n"
    
    # Learning trajectory
    content += "\n### Recent Activities\n\n"
    recent_activities = progress["learning_trajectory"][-5:][::-1]  # Last 5 activities
    for activity in recent_activities:
        content += f"**{activity['date']}** - Level {activity['level']}: {activity['activity']}\n"
        if activity['key_insights']:
            content += "  - Insights: " + ", ".join(activity['key_insights']) + "\n"
    
    # Next steps
    content += "\n### Next Steps\n\n"
    if progress["recommendations"]:
        last_recommendation = progress["recommendations"][-1]
        content += f"- **Recommended Level**: {last_recommendation['next_level']}\n"
        content += f"- **Focus**: {last_recommendation['focus']}\n"
        content += f"- **Preparation**: {last_recommendation['preparation']}\n"
    else:
        content += "- Continue your learning journey\n"
    
    # Write the index file
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Generated index file: {index_file}")
    return index_file


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Save learning progress with Socratic format")
    parser.add_argument("--base-path", required=True, help="Base directory for storing learning progress")
    parser.add_argument("--topic", required=True, help="Learning topic")
    parser.add_argument("--current-level", type=int, required=True, help="Current Bloom level (1-6)")
    parser.add_argument("--key-insights", nargs="*", default=[], help="Key insights from the session")
    parser.add_argument("--areas-for-improvement", nargs="*", default=[], help="Areas for improvement")
    parser.add_argument("--next-level", type=int, help="Recommended next level")
    parser.add_argument("--preparation-needed", default="Review current concepts", help="Preparation needed for next session")
    parser.add_argument("--session-plan", default="Continue learning", help="Plan for next session")
    parser.add_argument("--mastery-achieved", action="store_true", help="Whether mastery was achieved")
    parser.add_argument("--content", default="", help="Learning content for the article")
    parser.add_argument("--questions", nargs="*", default=[], help="Socratic questions for the article")
    
    args = parser.parse_args()
    
    # Create session data dictionary
    session_data = {
        "topic": args.topic,
        "current_level": args.current_level,
        "key_insights": args.key_insights,
        "areas_for_improvement": args.areas_for_improvement,
        "next_level": args.next_level,
        "preparation_needed": args.preparation_needed,
        "session_plan": args.session_plan,
        "mastery_achieved": args.mastery_achieved,
        "content": args.content,
        "questions": args.questions
    }
    
    # Create directory structure
    topic_dir = create_directory_structure(args.base_path, args.topic)
    
    # Get next article number
    article_number = get_next_article_number(topic_dir)
    
    # Create learning article
    create_learning_article(topic_dir, article_number, session_data)
    
    # Create feedback file
    create_feedback_file(topic_dir)
    
    # Update progress.json
    progress = update_progress_json(topic_dir, session_data, article_number)
    
    # Generate index.md
    generate_index_file(args.base_path, args.topic, progress)
    
    print("\nProgress saved successfully!")


if __name__ == "__main__":
    main()
