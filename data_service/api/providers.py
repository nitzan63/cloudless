from fastapi import APIRouter, HTTPException
from services.provider_service import ProviderService

router = APIRouter()
provider_service = ProviderService()

@router.post("/")
def create_provider(user_id: str, public_key: str):
    try:
        ip = provider_service.create_provider_with_ip(user_id, public_key)
        return {"status": "success", "ip": ip}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{provider_id}")
def get_provider(provider_id: int):
    provider = provider_service.get_provider(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Not found")
    return provider

@router.post("/{provider_id}/heartbeat")
def heartbeat(provider_id: int):
    provider_service.update_last_connection(provider_id)
    return {"status": "heartbeat updated"}
