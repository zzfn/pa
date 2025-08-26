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
                    "content": """你是一位精通股票市场价格行为学的金融分析师。接下来是一段相关的视频文字稿。

你的任务是提炼出其中最核心的观点和对交易者有用的信息。请以清晰、有条理的方式总结。如果文中包含以下方面的信息，请使用对应的标题进行组织：

*   **核心概念**: 视频中讲解的关键理论或原则。
*   **交易策略**: 提到的具体交易方法、形态或信号。
*   **市场分析**: 对某个股票或整体市场的分析。
*   **关键要点**: 对交易者最重要的建议。

如果某方面内容不存在，则忽略该标题。如果全文信息量较少，就给出一个简短的段落式总结即可。""",
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
