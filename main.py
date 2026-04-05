from fastapi import FastAPI, UploadFile, File
import fitz  # PyMuPDF

app = FastAPI()

# Index route
@app.get("/")
def read_root():
    print ("Hi people")
    return {"message": "Hello World"}

# Extract text from uploaded PDF
@app.post("/extract")
async def extract_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        return {"error": "Please upload a PDF file"}

    text_content = ""
    pdf = fitz.open(stream=await file.read(), filetype="pdf")
    for page in pdf:
        text_content += page.get_text() + "\n"
    pdf.close()

    return {"content": text_content}


@app.post("/chat-openrouter")
async def chat_openrouter(req: ChatRequest):
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        return {"error": "OPENROUTER_API_KEY not set"}

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openrouter/auto",
            "messages": [{"role": "user", "content": req.prompt}]
        },
        timeout=30
    )

    if response.status_code != 200:
        return {"error": response.text}

    return {
        "response": response.json()["choices"][0]["message"]["content"]
    }