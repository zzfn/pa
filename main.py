import os
import inquirer
from dotenv import load_dotenv
from transcribe import run_transcription
from summarize import run_summarization

def main():
    """
    Main entry point for the audio transcription and summarization tool.
    """
    load_dotenv()

    # Define directories
    audio_dir = "audio"
    transcripts_dir = "transcripts"
    summaries_dir = "summaries"

    # Ensure directories exist
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(transcripts_dir, exist_ok=True)
    os.makedirs(summaries_dir, exist_ok=True)

    # Ask user for action
    questions = [
        inquirer.List('action',
                        message="请选择要执行的操作",
                        choices=['transcribe', 'summarize'],
                    ),
    ]
    answers = inquirer.prompt(questions)
    if not answers:
        return
    action = answers['action']

    if action == "transcribe":
        run_transcription(audio_dir, transcripts_dir)
    elif action == "summarize":
        run_summarization(transcripts_dir, summaries_dir)

if __name__ == "__main__":
    main()
