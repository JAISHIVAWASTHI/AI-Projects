from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from fastapi import File, UploadFile
from fastapi.responses import JSONResponse
from object_detection import OBJECT_DETECTION
import base64

app = FastAPI()
UPLOAD_FOLDER = "uploaded_images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Save the uploaded image
        file_path = os.path.join(UPLOAD_FOLDER, "image1.jpg")
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        print(file_path)

        # Check if the file exists and process it
        if os.path.exists(file_path):
            print("Processing image...")
            model_object = OBJECT_DETECTION(file_path)
            output = model_object.wrapper_function()
            print(output)

        # Encode another image as Base64
        other_image_path = "./object-detection.jpg"  # Update this path
        with open(other_image_path, "rb") as img_file:
            other_image_base64 = base64.b64encode(img_file.read()).decode("utf-8")

        return JSONResponse(
            content={
                "message": "Image uploaded successfully!",
                "file_path": file_path,
                "output": output,
                "other_image": other_image_base64,
            },
            status_code=200,
        )
    except Exception as e:
        return JSONResponse(
            content={"message": f"An error occurred: {str(e)}"}, status_code=500
        )
