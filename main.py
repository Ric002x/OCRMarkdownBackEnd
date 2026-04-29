import asyncio
from fastapi import FastAPI, UploadFile
from docling.document_converter import DocumentConverter, DocumentStream
import io
from concurrent.futures import ProcessPoolExecutor
from fastapi.middleware.cors import CORSMiddleware

executor = ProcessPoolExecutor(max_workers=2)

api = FastAPI(
    title="File Conversion Application",
)

origins = ['*']

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def ocr_and_markdown_files(file, export_type='txt'):
    converter = DocumentConverter()
    result = converter.convert(file)
    doc = result.document

    if export_type == "md":
        texto = doc.export_to_markdown()
    elif export_type == "html":
        texto = doc.export_to_html()
    else:
        texto = doc.export_to_text()

    return texto


@api.get('/')
async def home():
    return "hello word"


@api.post("/ocr")
async def ocr(file: UploadFile):
    if not file.filename:
        return {}

    file_content = await file.read()
    file_stream = io.BytesIO(file_content)

    source = DocumentStream(name=file.filename, stream=file_stream)

    # Roda o processamento pesado sem travar o loop de eventos do FastAPI
    # loop = asyncio.get_event_loop()
    # result = await loop.run_in_executor(None, ocr_and_markdown_files, source)

    result = await asyncio.to_thread(
        ocr_and_markdown_files,
        source
    )

    return {"filename": file.filename, "content": result}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(api, host="0.0.0.0", port=8000)
