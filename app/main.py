from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import Response
from PIL import Image, ImageOps
import io

app = FastAPI(
    title="Pixel Art API",
    description="이미지를 업로드하면 픽셀아트(도트) 스타일로 변환해주는 API입니다.",
    version="1.0.0"
)

@app.post("/convert/")
async def convert_to_pixel_art(
    file: UploadFile = File(...),
    pixel_size: int = Form(32, description="픽셀 크기 (기본값: 32)"),
    grayscale: bool = Form(False, description="흑백 변환 여부"),
    invert: bool = Form(False, description="색상 반전 여부")
):
    """
    업로드된 이미지를 픽셀 크기로 축소한 후 원래 크기로 확대(Nearest Neighbor)하여
    도트(픽셀아트) 스타일로 변환합니다.
    추가로 흑백 전환 및 색상 반전 옵션을 제공합니다.
    """
    # 업로드된 파일 읽기
    contents = await file.read()
    
    try:
        # PIL 이미지로 열기
        image = Image.open(io.BytesIO(contents))
        output_format = image.format if image.format else 'PNG'
        
        # 처리 편의를 위해 RGBA 등 포맷인 경우 RGB로 변환 (반전 등을 위해)
        if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
            background = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode == 'RGBA':
                background.paste(image, mask=image.split()[3])
            else:
                background.paste(image.convert("RGBA"), mask=image.convert("RGBA").split()[3])
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
            
        # 그레이스케일 적용
        if grayscale:
            image = ImageOps.grayscale(image).convert('RGB')
            
        # 색상 반전 적용
        if invert:
            image = ImageOps.invert(image)

        # 원본 이미지 크기 저장
        original_size = image.size
        
        # 1차: 입력받은 pixel_size 픽셀로 축소 (디테일 정보 손실 발생 -> 도트 느낌 생성)
        # 만약 입력받은 pixel_size가 0 이하로 들어오면 기본값 32로 방어지원
        p_size = pixel_size if pixel_size > 0 else 32
        small_image = image.resize((p_size, p_size), resample=Image.Resampling.BILINEAR)
        
        # 2차: 원래 크기로 다시 확대
        # NEAREST를 사용하여 안티앨리어싱 없이 픽셀의 각진 느낌을 살림
        pixel_image = small_image.resize(original_size, resample=Image.Resampling.NEAREST)
        
        # 변환된 이미지를 바이트로 변환
        img_byte_arr = io.BytesIO()
        pixel_image.save(img_byte_arr, format=output_format)
        img_byte_arr.seek(0)
        
        # 응답 헤더에 적용된 옵션 메타데이터 포함 (기존 Response 객체 구조 유지)
        headers = {
            "X-Applied-Pixel-Size": str(p_size),
            "X-Applied-Grayscale": str(grayscale).lower(),
            "X-Applied-Invert": str(invert).lower()
        }
        
        return Response(content=img_byte_arr.getvalue(), media_type=f"image/{output_format.lower()}", headers=headers)
        
    except Exception as e:
        return {"error": "이미지 처리 중 오류가 발생했습니다.", "detail": str(e)}

@app.get("/")
def read_root():
    return {"message":"CD test"}
