import anthropic
import json
import os
import asyncio
import edge_tts
from pydub import AudioSegment

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

FEMALE_VOICE = "en-US-JennyNeural"
MALE_VOICE = "en-GB-RyanNeural"

def call_claude(prompt):
    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        text = message.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except Exception as e:
        print(f"Claude API Error: {e}")
        raise e

def generate_listening_test():
    return call_claude("""Generate a realistic IELTS listening test conversation between two people.
    Write each person's lines separately, one per line, alternating between the two speakers.
    NO names, NO labels, NO indicators of who is speaking. Just the spoken words alternating.
    First line is always the female speaker, second line is male, third female etc.
    Respond ONLY with this exact JSON format, no other text:
    {
        "script": "Hello, I was wondering if you could help me.\\nOf course! What do you need?\\nI am looking for information about the evening courses.\\nSure, we have several options available.\\nCould you tell me about the schedule?\\nYes, classes run from Monday to Friday, 6pm to 9pm.",
        "questions": [
            {"question": "Question 1?", "options": ["A) opt1", "B) opt2", "C) opt3", "D) opt4"], "answer": "A"},
            {"question": "Question 2?", "options": ["A) opt1", "B) opt2", "C) opt3", "D) opt4"], "answer": "B"},
            {"question": "Question 3?", "options": ["A) opt1", "B) opt2", "C) opt3", "D) opt4"], "answer": "C"},
            {"question": "Question 4?", "options": ["A) opt1", "B) opt2", "C) opt3", "D) opt4"], "answer": "A"},
            {"question": "Question 5?", "options": ["A) opt1", "B) opt2", "C) opt3", "D) opt4"], "answer": "B"}
        ]
    }""")

async def generate_voice(text, voice, filename):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filename)

async def create_dual_voice_audio(script, output_filename):
    lines = [line.strip() for line in script.split('\n') if line.strip()]
    temp_files = []

    for i, line in enumerate(lines):
        voice = FEMALE_VOICE if i % 2 == 0 else MALE_VOICE
        temp_file = f"temp_{i}.mp3"
        await generate_voice(line, voice, temp_file)
        temp_files.append(temp_file)

    # Combine all audio files
    combined = AudioSegment.empty()
    pause = AudioSegment.silent(duration=500)

    for temp_file in temp_files:
        segment = AudioSegment.from_mp3(temp_file)
        combined += segment + pause

    combined.export(output_filename, format="mp3")

    # Clean up temp files
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            os.remove(temp_file)

    return output_filename

async def text_to_audio(text, filename):
    await create_dual_voice_audio(text, filename)
    return filename

def generate_reading_test():
    return call_claude("""Generate an IELTS reading passage (150-200 words) and 5 questions.
    Respond ONLY with this exact JSON format, no other text:
    {
        "passage": "Reading passage here",
        "questions": [
            {"question": "Question 1?", "options": ["A) opt1", "B) opt2", "C) opt3", "D) opt4"], "answer": "A"},
            {"question": "Question 2?", "options": ["A) opt1", "B) opt2", "C) opt3", "D) opt4"], "answer": "B"},
            {"question": "Question 3?", "options": ["A) opt1", "B) opt2", "C) opt3", "D) opt4"], "answer": "C"},
            {"question": "Question 4?", "options": ["A) opt1", "B) opt2", "C) opt3", "D) opt4"], "answer": "A"},
            {"question": "Question 5?", "options": ["A) opt1", "B) opt2", "C) opt3", "D) opt4"], "answer": "B"}
        ]
    }""")

def generate_grammar_lesson():
    return call_claude("""Generate an IELTS grammar lesson.
    Respond ONLY with this exact JSON format, no other text:
    {
        "topic": "Grammar topic",
        "explanation": "Clear explanation here",
        "examples": ["Example 1", "Example 2"],
        "questions": [
            {"question": "Question 1?", "options": ["A) opt1", "B) opt2", "C) opt3", "D) opt4"], "answer": "A"},
            {"question": "Question 2?", "options": ["A) opt1", "B) opt2", "C) opt3", "D) opt4"], "answer": "B"},
            {"question": "Question 3?", "options": ["A) opt1", "B) opt2", "C) opt3", "D) opt4"], "answer": "C"}
        ]
    }""")

def generate_vocabulary_lesson():
    return call_claude("""Generate an IELTS vocabulary lesson with 5 advanced words.
    Respond ONLY with this exact JSON format, no other text:
    {
        "topic": "Vocabulary topic",
        "words": [
            {"word": "word1", "definition": "meaning", "example": "example sentence"},
            {"word": "word2", "definition": "meaning", "example": "example sentence"},
            {"word": "word3", "definition": "meaning", "example": "example sentence"},
            {"word": "word4", "definition": "meaning", "example": "example sentence"},
            {"word": "word5", "definition": "meaning", "example": "example sentence"}
        ],
        "questions": [
            {"question": "Question 1?", "options": ["A) opt1", "B) opt2", "C) opt3", "D) opt4"], "answer": "A"},
            {"question": "Question 2?", "options": ["A) opt1", "B) opt2", "C) opt3", "D) opt4"], "answer": "B"},
            {"question": "Question 3?", "options": ["A) opt1", "B) opt2", "C) opt3", "D) opt4"], "answer": "C"}
        ]
    }""")

def generate_writing_tips():
    return call_claude("""Generate IELTS Writing Task 2 tips.
    Respond ONLY with this exact JSON format, no other text:
    {
        "topic": "Essay topic",
        "tips": ["Tip 1", "Tip 2", "Tip 3"],
        "template": "Essay template structure",
        "sample_intro": "Sample introduction paragraph"
    }""")

def generate_speaking_tips():
    return call_claude("""Generate an IELTS speaking practice question with tips.
    Respond ONLY with this exact JSON format, no other text:
    {
        "question": "Speaking question",
        "tips": ["Tip 1", "Tip 2", "Tip 3"],
        "sample_answer": "Sample answer here",
        "useful_phrases": ["Phrase 1", "Phrase 2", "Phrase 3"]
    }""")

def generate_uzbek_lesson():
    return call_claude("""Generate a basic English lesson for Uzbek speakers learning English for IELTS.
    Respond ONLY with this exact JSON format, no other text:
    {
        "topic": "Lesson topic in Uzbek",
        "explanation": "Explanation in Uzbek language",
        "examples": ["Example 1 with Uzbek translation", "Example 2 with Uzbek translation"],
        "questions": [
            {"question": "Question in Uzbek?", "options": ["A) opt1", "B) opt2", "C) opt3", "D) opt4"], "answer": "A"},
            {"question": "Question 2 in Uzbek?", "options": ["A) opt1", "B) opt2", "C) opt3", "D) opt4"], "answer": "B"},
            {"question": "Question 3 in Uzbek?", "options": ["A) opt1", "B) opt2", "C) opt3", "D) opt4"], "answer": "C"}
        ]
    }""")

def generate_russian_lesson():
    return call_claude("""Generate a basic English lesson for Russian speakers learning English for IELTS.
    Respond ONLY with this exact JSON format, no other text:
    {
        "topic": "Lesson topic in Russian",
        "explanation": "Explanation in Russian language",
        "examples": ["Example 1 with Russian translation", "Example 2 with Russian translation"],
        "questions": [
            {"question": "Question in Russian?", "options": ["A) opt1", "B) opt2", "C) opt3", "D) opt4"], "answer": "A"},
            {"question": "Question 2 in Russian?", "options": ["A) opt1", "B) opt2", "C) opt3", "D) opt4"], "answer": "B"},
            {"question": "Question 3 in Russian?", "options": ["A) opt1", "B) opt2", "C) opt3", "D) opt4"], "answer": "C"}
        ]
    }""")

def get_band_score(score, total):
    percentage = (score / total) * 100
    if percentage >= 90:
        return "8.5 - 9.0"
    elif percentage >= 80:
        return "7.5 - 8.0"
    elif percentage >= 70:
        return "6.5 - 7.0"
    elif percentage >= 60:
        return "5.5 - 6.0"
    elif percentage >= 50:
        return "4.5 - 5.0"
    else:
        return "Below 4.5"