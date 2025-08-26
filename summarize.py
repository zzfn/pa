import os
import inquirer
from openai import OpenAI
from dotenv import load_dotenv

def run_summarization(transcripts_dir="transcripts", summaries_dir="summaries"):
    """
    Handles the AI summarization process.
    """
    load_dotenv()
    
    # List files in the transcripts directory
    try:
        transcript_files = [f for f in os.listdir(transcripts_dir) if f.endswith(".txt")]
        if not transcript_files:
            print(f"在 '{transcripts_dir}' 目录中没有找到转录文件。")
            return
    except FileNotFoundError:
        print(f"目录 '{transcripts_dir}' 不存在。")
        return

    # Ask user to choose a file
    questions = [
        inquirer.List('selected_file',
                        message="请选择要总结的转录文件",
                        choices=transcript_files,
                    ),
    ]
    answers = inquirer.prompt(questions)
    if not answers:
        return
    selected_file = answers['selected_file']
    
    transcript_path = os.path.join(transcripts_dir, selected_file)

    print(f"正在读取文件 {transcript_path} 并进行AI总结...")

    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            transcript_text = f.read()

        # Initialize OpenAI client for OpenRouter
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )

        # Create chat completion
        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct",
            messages=[
                {
                    "role": "system",
                    "content": """你是一位顶级的金融分析师和交易导师，专精于股票市场的价格行为学。你的任务是将下面的视频文字稿，转换成一份详尽、清晰、高度可读的学习笔记。

请通读全文，理解其核心主题与逻辑脉络，然后完全根据内容本身，自行设计最合理的结构，使用恰当的标题、子标题和列表来呈现。在总结时，请修正原文中可能的错别字和语病，确保最终输出的语句通顺、专业。

唯一需要遵守的特殊规则是：如果文中出现了值得解释的专业术语，请在笔记的末尾创建一个名为【专业术语解释】的独立部分，并对其进行简要说明。

你的目标是产出一份能真正帮助交易者学习和吸收视频精华的、高质量的文档。请务必使用简体中文进行总结。""",
                },
                {"role": "user", "content": transcript_text},
            ],
        )
        
        summary = response.choices[0].message.content

        print("\n--- AI 总结 ---")
        print(summary)
        print("-----------------")

        # Save the summary
        summary_filename = os.path.splitext(selected_file)[0] + "_summary.txt"
        summary_path = os.path.join(summaries_dir, summary_filename)

        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary)

        print(f"总结已保存到 {summary_path}")

    except FileNotFoundError:
        print(f"文件未找到: {transcript_path}")
    except Exception as e:
        print(f"AI总结过程中发生错误: {e}")

if __name__ == '__main__':
    # To allow running this file directly for testing
    os.makedirs("transcripts", exist_ok=True)
    os.makedirs("summaries", exist_ok=True)
    run_summarization()
