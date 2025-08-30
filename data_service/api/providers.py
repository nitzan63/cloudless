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

@router.get("/{user_id}")
def get_provider(user_id: str):
    provider = provider_service.get_provider(user_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Not found")
    return provider

@router.get("/")
def get_all_providers():
    providers = provider_service.get_all_providers()
    return providers

@router.post("/{provider_id}/heartbeat")
def heartbeat(provider_id: int):
    provider_service.update_last_connection(provider_id)
    return {"status": "heartbeat updated"}

@router.post("/credits/add")
def add_credits(payload: dict):
    network_ips = payload.get("network_ips")
    amount = payload.get("amount")
    if network_ips is None or amount is None:
        raise HTTPException(status_code=400, detail="network_ips and amount are required")
    if isinstance(network_ips, str):
        network_ips = [network_ips]
    if not isinstance(network_ips, list) or not all(isinstance(x, str) for x in network_ips):
        raise HTTPException(status_code=400, detail="network_ips must be a list of strings")
    try:
        amount = int(amount)
    except Exception:
        raise HTTPException(status_code=400, detail="amount must be an integer")
    if amount == 0:
        return {"status": "no change", "network_ips": network_ips}
    results = provider_service.add_credits_by_ip(network_ips, amount)
    if not results:
        raise HTTPException(status_code=404, detail="No providers found for given IPs")
    return {"status": "success", "updated": results}
