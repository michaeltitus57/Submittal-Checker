from fastapi import FastAPI

app = FastAPI(title="Submittal Checker")

@app.get("/health")
def health():
    return {"status": "ok"}
