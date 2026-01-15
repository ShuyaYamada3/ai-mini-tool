import os
from dotenv import load_dotenv
from google import genai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field # Fieldを追加（詳細説明用）
from fastapi.middleware.cors import CORSMiddleware

# .env読み込み
load_dotenv()

# --- 設定周り ---
app = FastAPI(
    title="AI ミニツール API",  # 日本語タイトルに変更
    description="生成AIを用いたテキスト要約や文章校正を行います。",
    version="1.0.0"
)

# フロントエンド連携用の許可設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Geminiクライアント設定
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# --- データモデル定義 ---
class TextRequest(BaseModel):
    text: str = Field(..., title="入力テキスト", description="AIに処理させたい文章を入力してください")

class AIResponse(BaseModel):
    result: str = Field(..., title="AIの回答", description="AIによって生成された結果テキスト")

# --- AI処理の共通関数 ---
def call_gemini(system_prompt: str, user_text: str) -> str:
    if not client:
        raise HTTPException(status_code=500, detail="API Key not configured")
    try:
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=f"{system_prompt}\n\n対象テキスト:\n{user_text}"
        )
        return response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- APIのエンドポイント ---

@app.get("/", summary="API稼働確認", description="APIが正常に動いているか確認します。")
def read_root():
    return {"message": "AI Mini Tool API は正常に稼働しています！"}

@app.post("/summarize", response_model=AIResponse, summary="テキスト要約機能", description="長い文章を受け取り、箇条書きで要点をまとめます。")
def api_summarize(request: TextRequest):
    """
    **テキスト要約API**
    - 入力: 長文テキスト
    - 出力: 3点の箇条書き要約
    """
    system_prompt = "あなたは優秀な編集者です。入力されたテキストの要点を抽出し、3箇条書きで簡潔に要約してください。"
    output = call_gemini(system_prompt, request.text)
    return {"result": output}

@app.post("/proofread", response_model=AIResponse, summary="文章校正機能", description="誤字脱字を修正し、ビジネスメールに適した敬語に変換します。")
def api_proofread(request: TextRequest):
    """
    **文章校正API**
    - 入力: ラフな文章
    - 出力: ビジネス敬語に修正された文章
    """
    system_prompt = "あなたはプロのライターです。入力されたテキストの誤字脱字を修正し、ビジネスメールとして適切な敬語に直してください。"
    output = call_gemini(system_prompt, request.text)
    return {"result": output}
