import pickle
import re
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from deep_translator import GoogleTranslator
from transformers import pipeline

# Initialize the Hugging Face summarizer
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

def get_available_languages(video_id):
    """Fetch available transcript languages for a YouTube video."""
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        return {t.language: t.language_code for t in transcript_list}
    except Exception:
        return None

def chunk_text(text, chunk_size=300):
    """Splits text into smaller chunks for summarization."""
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i+chunk_size])

def translate_text(text, target_lang="en"):
    """Translates text to the target language using Google Translator."""
    try:
        return GoogleTranslator(source='auto', target=target_lang).translate(text)
    except Exception as e:
        print(f"Error during translation: {e}")
        return text

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

def get_user_inputs():
    """Handles user inputs for URL and summary length."""
    url = input("\nEnter YouTube Video URL: ").strip()
    video_id = get_video_id(url)
    if not video_id:
        print("⚠️ Invalid YouTube URL!")
        return None, None

    print("Fetching available languages...")
    languages = get_available_languages(video_id)

    if not languages:
        print("Could not retrieve available languages.")
        lang_choice = "en"
    else:
        print("\nAvailable languages:")
        for lang, code in languages.items():
            print(f"{lang} ({code})")
        lang_choice = "en"  # Automatically set to English

    # Exit if the language is not English
    if lang_choice != "en":
        print("This video is not in English. Please enter a new YouTube URL.")
        return None, None

    print("\nFetching transcript...")
    transcript = fetch_transcript(video_id, lang_choice)
    if "Error" in transcript:
        print(transcript)
        return None, None

    print(f"\nTranscript Length: {len(transcript.split())} words")

    # Get word limit for summarization
    while True:
        try:
            max_words = int(input("\nEnter the number of words for the summary: ").strip())
            if max_words > 0:
                break
            else:
                print("⚠️ Please enter a positive integer.")
        except ValueError:
            print("⚠️ Invalid input! Please enter a valid number.")

    return transcript, max_words

def main():
    """Main loop for summarization app."""
    while True:
        transcript, max_words = get_user_inputs()
        if not transcript:
            continue  # Restart if transcript failed

        summary = summarize_transcript(transcript, max_words)

        print("\n📌 **Summary:**")
        print(summary)
        print(f"\n📏 Summary Length: {len(summary.split())} words")

        # Ask user what to do next
        while True:
            print("\n🔄 What would you like to do next?")
            print("1️⃣ Change word count and re-summarize")
            print("2️⃣ Enter a new YouTube URL")
            print("3️⃣ Exit")

            choice = input("Enter your choice (1/2/3): ").strip()

            if choice == "1":
                while True:
                    try:
                        new_max_words = int(input("Enter new word count: ").strip())
                        if new_max_words > 0:
                            break
                        else:
                            print("⚠️ Please enter a positive integer.")
                    except ValueError:
                        print("⚠️ Invalid input! Please enter a valid number.")

                summary = summarize_transcript(transcript, new_max_words)
                print("\n📌 **Updated Summary:**")
                print(summary)
                print(f"\n📏 Summary Length: {len(summary.split())} words")

            elif choice == "2":
                break  # Restart with a new URL

            elif choice == "3":
                print("👋 Exiting... Thank you!")
                return

            else:
                print("⚠️ Invalid choice. Please enter 1, 2, or 3.")

# Run the app
main()
with open("summarizer.pkl", "wb") as f:
    pickle.dump(summarizer, f)