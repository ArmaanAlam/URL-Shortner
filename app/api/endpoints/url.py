from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.api.deps import get_shortener_service
from app.services.shortener_service import URLShortenerService
from app.schemas.url import ShortenRequest, ShortenResponse, URLStatsResponse
from app.core.exceptions import InvalidURLException, AliasConflictException, URLNotFoundException

router = APIRouter(prefix="/api", tags=["URL Operations"])

@router.post("/shorten", response_model=ShortenResponse, status_code=status.HTTP_201_CREATED)
def shorten_url(
    payload: ShortenRequest,
    request: Request,
    service: URLShortenerService = Depends(get_shortener_service)
):
    try:
        result = service.shorten_url(raw_url=payload.url, custom_alias=payload.custom_alias)
        base_host = str(request.base_url).rstrip("/")
        return {
            "short_url": f"{base_host}/{result['short_key']}",
            "short_key": result["short_key"],
            "original_url": result["original_url"],
            "created_at": result["created_at"]
        }
    except InvalidURLException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except AliasConflictException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.get("/stats/{key}", response_model=URLStatsResponse)
def get_stats(
    key: str,
    service: URLShortenerService = Depends(get_shortener_service)
):
    try:
        return service.get_stats(key)
    except URLNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
