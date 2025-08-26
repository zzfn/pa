import os
import whisper
import inquirer

def run_transcription(audio_dir="audio", transcripts_dir="transcripts"):
    """
    Handles the audio transcription process.
    """
    # List files in the audio directory
    try:
        audio_files = [f for f in os.listdir(audio_dir) if os.path.isfile(os.path.join(audio_dir, f))]
        if not audio_files:
            print(f"在 '{audio_dir}' 目录中没有找到音频文件。")
            return
    except FileNotFoundError:
        print(f"目录 '{audio_dir}' 不存在。")
        return

    # Ask user to choose a file
    questions = [
        inquirer.List('selected_file',
                        message="请选择要转录的音频文件",
                        choices=audio_files,
                    ),
    ]
    answers = inquirer.prompt(questions)
    if not answers:
        return
    selected_file = answers['selected_file']

    # Transcribe the audio file
    audio_path = os.path.join(audio_dir, selected_file)
    print(f"正在加载模型并转录 {audio_path}...")

    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_path, verbose=True)
        transcript = result["text"]

        # Save the transcript
        transcript_filename = os.path.splitext(selected_file)[0] + ".txt"
        transcript_path = os.path.join(transcripts_dir, transcript_filename)

        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript)

        print(f"转录完成！结果已保存到 {transcript_path}")

    except Exception as e:
        print(f"转录过程中发生错误: {e}")

if __name__ == '__main__':
    # To allow running this file directly for testing
    os.makedirs("audio", exist_ok=True)
    os.makedirs("transcripts", exist_ok=True)
    run_transcription()
