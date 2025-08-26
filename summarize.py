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

    # Create a list of choices with status
    choices_with_status = []
    for filename in transcript_files:
        # Check for summary file with .md extension
        base_filename = os.path.splitext(filename)[0]
        summary_filename_md = base_filename + ".md"
        summary_path = os.path.join(summaries_dir, summary_filename_md)
        status = "✓ 已总结" if os.path.exists(summary_path) else "✗ 未总结"
        choices_with_status.append(f"{filename} ({status})")

    # Ask user to choose a file
    questions = [
        inquirer.List('selected_choice',
                        message="请选择要总结的转录文件",
                        choices=choices_with_status,
                    ),
    ]
    answers = inquirer.prompt(questions)
    if not answers:
        return
    
    # Extract the original filename from the choice
    selected_choice = answers['selected_choice']
    selected_file = selected_choice.split(" (")[0]
    
    # Determine output path with .md extension
    base_filename = os.path.splitext(selected_file)[0]
    summary_filename_md = base_filename + ".md"
    summary_path = os.path.join(summaries_dir, summary_filename_md)

    transcript_path = os.path.join(transcripts_dir, selected_file)

    print(f"正在准备AI总结...")

    try:
        print(f"[1/5] 读取转录文件: {transcript_path}")
        with open(transcript_path, "r", encoding="utf-8") as f:
            transcript_text = f.read()
        print("[2/5] 文件读取完毕。")

        print("[3/5] 初始化AI客户端...")
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        print("[4/5] 客户端初始化完毕。正在向AI发送请求，请稍候...")

        # Create chat completion
        response = client.chat.completions.create(
            model="google/gemini-2.5-flash",
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
        
        print("[5/5] AI响应成功！正在处理和保存总结...")
        summary = response.choices[0].message.content

        print("\n--- AI 总结 ---")
        print(summary)
        print("-----------------")

        # Save the summary
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary)

        print(f"总结已保存到 {summary_path}")

    except FileNotFoundError:
        print(f"错误: 文件未找到: {transcript_path}")
    except Exception as e:
        print(f"错误: AI总结过程中发生严重错误: {e}")




if __name__ == '__main__':
    # To allow running this file directly for testing
    os.makedirs("transcripts", exist_ok=True)
    os.makedirs("summaries", exist_ok=True)
    run_summarization()
