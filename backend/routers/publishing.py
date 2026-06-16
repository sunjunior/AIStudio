from fastapi import APIRouter, HTTPException

from ..schemas.publishing import PublishCreate, PublishResponse, PublishListResponse
from ..services.publisher import Publisher

router = APIRouter(prefix="/api/publishing", tags=["publishing"])
publisher = Publisher()


@router.post("", response_model=PublishResponse, status_code=201)
async def create_publish(body: PublishCreate):
    try:
        if body.service_type == "export":
            export_path = body.config.get("export_path", "")
            if not export_path:
                raise HTTPException(400, "export_path required for export")
            service = await publisher.publish_export(
                model_id=body.model_id,
                export_path=export_path,
            )
        else:
            service = await publisher.publish(
                model_id=body.model_id,
                service_type=body.service_type,
                publish_config=body.config,
            )
        return PublishResponse.model_validate(service)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("", response_model=PublishListResponse)
def list_services():
    services = publisher.list_services()
    return PublishListResponse(
        services=[PublishResponse.model_validate(s) for s in services],
        total=len(services),
    )


@router.get("/{service_id}", response_model=PublishResponse)
def get_service(service_id: int):
    service = publisher.get_service(service_id)
    if not service:
        raise HTTPException(404, f"Service id={service_id} not found")
    return PublishResponse.model_validate(service)


@router.post("/{service_id}/stop")
async def stop_service(service_id: int):
    try:
        await publisher.stop_service(service_id)
        return {"success": True}
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.delete("/{service_id}")
async def delete_service(service_id: int):
    try:
        await publisher.delete_service(service_id)
        return {"success": True}
    except ValueError as e:
        raise HTTPException(400, str(e))
