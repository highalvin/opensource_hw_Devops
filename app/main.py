from fastapi import FastAPI, File, UploadFile
from fastapi.responses import Response
from PIL import Image
import io

app = FastAPI(
    title="Pixel Art API",
    description="이미지를 업로드하면 픽셀아트(도트) 스타일로 변환해주는 API입니다.",
    version="1.0.0"
)

@app.post("/convert/")
async def convert_to_pixel_art(file: UploadFile = File(...)):
    """
    업로드된 이미지를 32x32 크기로 축소한 후 원래 크기로 확대(Nearest Neighbor)하여
    도트(픽셀아트) 스타일로 변환합니다.
    """
    # 업로드된 파일 읽기
    contents = await file.read()
    
    try:
        # PIL 이미지로 열기
        image = Image.open(io.BytesIO(contents))
        
        # 원본 이미지 크기 저장
        original_size = image.size
        
        # 1차: 32x32 픽셀로 축소 (디테일 정보 손실 발생 -> 도트 느낌 생성)
        # resample 옵션으로 BILINEAR 또는 BICUBIC을 사용하여 자연스럽게 축소
        small_image = image.resize((32, 32), resample=Image.Resampling.BILINEAR)
        
        # 2차: 원래 크기로 다시 확대
        # NEAREST를 사용하여 안티앨리어싱 없이 픽셀의 각진 느낌을 살림
        pixel_image = small_image.resize(original_size, resample=Image.Resampling.NEAREST)
        
        # 변환된 이미지를 바이트로 변환
        img_byte_arr = io.BytesIO()
        output_format = image.format if image.format else 'PNG'
        pixel_image.save(img_byte_arr, format=output_format)
        img_byte_arr.seek(0)
        
        return Response(content=img_byte_arr.getvalue(), media_type=f"image/{output_format.lower()}")
        
    except Exception as e:
        return {"error": "이미지 처리 중 오류가 발생했습니다.", "detail": str(e)}

@app.get("/")
def read_root():
    return {"message": "Pixel Art API 서버가 정상적으로 실행 중입니다. /docs 에서 API 문서를 확인하세요."}
