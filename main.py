import sys
import os
from dotenv import load_dotenv
from google import genai

# .envファイルから環境変数を読み込む
load_dotenv()

def get_gemini_client():
    """Geminiクライアントを初期化して返す"""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("警告: .envファイルに GEMINI_API_KEY が設定されていません。")
        return None
    return genai.Client(api_key=api_key)

def show_menu():
    """メニューを表示する関数"""
    print("\n=== AI Mini Tool (Latest SDK Ver) ===")
    print("1. テキスト要約")
    print("2. 文章校正")
    print("q. 終了")
    print("=====================================")

def get_ai_response(client, system_prompt, user_text):
    """Gemini APIを呼び出す共通関数"""
    if not client:
        return "エラー: APIキーが設定されていないため実行できません。"

    try:
        print("Wait a moment... AI is thinking...")
        
        # システムプロンプトを含めたリクエストを作成
        # 最新のgoogle-genaiライブラリの書き方
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=f"{system_prompt}\n\n対象テキスト:\n{user_text}"
        )
        return response.text
    except Exception as e:
        return f"APIエラーが発生しました: {e}"

def summarize_text(client):
    """要約機能"""
    print("\n--- テキスト要約 ---")
    # ここでは記事を貼り付けず、Enterを押す
    print("要約したいテキストを入力してください（入力後Enter）:")
    text = input("> ")
    
    if not text:
        print("テキストが空でした。メニューに戻ります。")
        return

    system_prompt = "あなたは優秀な編集者です。入力されたテキストの要点を抽出し、3箇条書きで簡潔に要約してください。"
    result = get_ai_response(client, system_prompt, text)
    
    print(f"\n[AIの回答]\n{result}")

def proofread_text(client):
    """校正機能"""
    print("\n--- 文章校正 ---")
    print("校正したいテキストを入力してください（入力後Enter）:")
    text = input("> ")

    if not text:
        print("テキストが空でした。メニューに戻ります。")
        return

    system_prompt = "あなたはプロのライターです。入力されたテキストの誤字脱字を修正し、ビジネスメールとして適切な敬語に直してください。"
    result = get_ai_response(client, system_prompt, text)
    
    print(f"\n[AIの回答]\n{result}")

def main():
    """メイン実行関数"""
    client = get_gemini_client()

    while True:
        show_menu()
        # ここでは「1」か「2」だけを入力する！記事はまだ貼らない！
        choice = input("機能を選択してください (1/2/q): ")

        if choice == '1':
            summarize_text(client)
        elif choice == '2':
            proofread_text(client)
        elif choice == 'q':
            print("アプリを終了します。")
            break
        else:
            print("無効な入力です。「1」「2」「q」のどれかを入力してください。")

if __name__ == "__main__":
    main()
