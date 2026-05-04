from fastapi import FastAPI

app = FastAPI(title="API Yfood", description="API de gestão de pedidos")

@app.get("/")
def health_check():
    return {"status": "ok"}
