'''
import pickle
import re
from flask import Flask, request, jsonify, render_template
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from deep_translator import GoogleTranslator
from transformers import pipeline

app = Flask(__name__)

# Load the summarizer from pickle file (if already saved)
try:
    with open("summarizer.pkl", "rb") as f:
        summarizer = pickle.load(f)
except FileNotFoundError:
    summarizer = pipeline("summarization")

def get_video_id(url):
    """Extracts the YouTube video ID from a URL."""
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def fetch_transcript(video_id, language='en'):
    """Fetch transcript from YouTube video."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        return " ".join([segment['text'] for segment in transcript])
    except TranscriptsDisabled:
        return "Error: Transcripts are disabled for this video."
    except Exception as e:
        return f"Error fetching transcript: {e}"

def chunk_text(text, chunk_size=300):
    """Splits text into smaller chunks for summarization."""
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i+chunk_size])

def summarize_transcript(transcript, max_words):
    """Summarizes transcript based on the desired word limit."""
    chunks = list(chunk_text(transcript))  # Convert generator to list
    summaries = [summarizer(chunk, max_length=max_words * 2, min_length=40, do_sample=False)[0]['summary_text'] for chunk in chunks]

    # Combine summaries
    final_summary = " ".join(summaries)

    # Trim to exact word count
    final_summary_words = final_summary.split()
    if len(final_summary_words) > max_words:
        final_summary = " ".join(final_summary_words[:max_words])

    return final_summary

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    """API Endpoint to summarize a YouTube video transcript."""
    data = request.json
    url = data.get("url")
    max_words = data.get("max_words", 100)

    if not url:
        return jsonify({"error": "No URL provided!"}), 400

    video_id = get_video_id(url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL!"}), 400

    transcript = fetch_transcript(video_id, language="en")
    if "Error" in transcript:
        return jsonify({"error": transcript}), 400

    summary = summarize_transcript(transcript, max_words)

    return jsonify({
        "summary": summary,
        "summary_length": len(summary.split()),
        "original_length": len(transcript.split())
    })

if __name__ == '__main__':
    app.run(debug=True)
'''

'''
import os
import pickle
import re
from flask import Flask, request, jsonify, render_template
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from deep_translator import GoogleTranslator
from transformers import pipeline

app = Flask(__name__)

def merge_files(output_file, chunk_prefix, num_chunks):
    """Merges multiple part files into a single file."""
    with open(output_file, 'wb') as f:
        for i in range(num_chunks):
            part_file = f"{chunk_prefix}{i}"
            if os.path.exists(part_file):
                with open(part_file, 'rb') as part:
                    f.write(part.read())

# Merge summarizer.pkl from parts if not already merged
if not os.path.exists("summarizer.pkl"):
    merge_files("summarizer.pkl", "summarizer.pkl.part", 12)  # 12 parts (0-11)

# Load the summarizer from pickle file
try:
    with open("summarizer.pkl", "rb") as f:
        summarizer = pickle.load(f)
except FileNotFoundError:
    summarizer = pipeline("summarization")

def get_video_id(url):
    """Extracts the YouTube video ID from a URL."""
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def fetch_transcript(video_id, language='en'):
    """Fetch transcript from YouTube video."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        return " ".join([segment['text'] for segment in transcript])
    except TranscriptsDisabled:
        return "Error: Transcripts are disabled for this video."
    except Exception as e:
        return f"Error fetching transcript: {e}"

def chunk_text(text, chunk_size=300):
    """Splits text into smaller chunks for summarization."""
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i+chunk_size])

def summarize_transcript(transcript, max_words):
    """Summarizes transcript based on the desired word limit."""
    chunks = list(chunk_text(transcript))  # Convert generator to list
    summaries = [summarizer(chunk, max_length=max_words * 2, min_length=40, do_sample=False)[0]['summary_text'] for chunk in chunks]

    # Combine summaries
    final_summary = " ".join(summaries)

    # Trim to exact word count
    final_summary_words = final_summary.split()
    if len(final_summary_words) > max_words:
        final_summary = " ".join(final_summary_words[:max_words])

    return final_summary

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    """API Endpoint to summarize a YouTube video transcript."""
    data = request.json
    url = data.get("url")
    max_words = data.get("max_words", 100)

    if not url:
        return jsonify({"error": "No URL provided!"}), 400

    video_id = get_video_id(url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL!"}), 400

    transcript = fetch_transcript(video_id, language="en")
    if "Error" in transcript:
        return jsonify({"error": transcript}), 400

    summary = summarize_transcript(transcript, max_words)

    return jsonify({
        "summary": summary,
        "summary_length": len(summary.split()),
        "original_length": len(transcript.split())
    })

if __name__ == '__main__':
    app.run(debug=True)
'''
import pickle
import re
from flask import Flask, request, jsonify, render_template
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from deep_translator import GoogleTranslator
from transformers import pipeline

app = Flask(__name__)

# Load the summarizer from pickle file (if already saved)
try:
    with open("summarizer.pkl", "rb") as f:
        summarizer = pickle.load(f)
except (FileNotFoundError, EOFError):  # Handle missing or empty file
    summarizer = pipeline("summarization")
    with open("summarizer.pkl", "wb") as f:
        pickle.dump(summarizer, f)

def get_video_id(url):
    """Extracts the YouTube video ID from a URL."""
    pattern = r"(?:v=|/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def fetch_transcript(video_id, language='en'):
    """Fetch transcript from YouTube video."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        return " ".join([segment['text'] for segment in transcript])
    except TranscriptsDisabled:
        return "Error: Transcripts are disabled for this video."
    except Exception as e:
        return f"Error fetching transcript: {e}"

def chunk_text(text, chunk_size=300):
    """Splits text into smaller chunks for summarization."""
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i+chunk_size])

def summarize_transcript(transcript, max_words):
    """Summarizes transcript based on the desired word limit."""
    chunks = list(chunk_text(transcript))  # Convert generator to list
    summaries = [summarizer(chunk, max_length=max_words * 2, min_length=40, do_sample=False)[0]['summary_text'] for chunk in chunks]

    # Combine summaries
    final_summary = " ".join(summaries)

    # Trim to exact word count
    final_summary_words = final_summary.split()
    if len(final_summary_words) > max_words:
        final_summary = " ".join(final_summary_words[:max_words])

    return final_summary

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    """API Endpoint to summarize a YouTube video transcript."""
    data = request.json
    url = data.get("url")
    max_words = data.get("max_words", 100)

    if not url:
        return jsonify({"error": "No URL provided!"}), 400

    video_id = get_video_id(url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL!"}), 400

    transcript = fetch_transcript(video_id, language="en")
    if "Error" in transcript:
        return jsonify({"error": transcript}), 400

    summary = summarize_transcript(transcript, max_words)

    return jsonify({
        "summary": summary,
        "summary_length": len(summary.split()),
        "original_length": len(transcript.split())
    })

if __name__ == '__main__':
    app.run(debug=True)
