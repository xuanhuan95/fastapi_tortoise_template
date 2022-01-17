from fastapi import APIRouter, Depends


router = APIRouter(
    prefix="/order_status",
    tags=["order_status"],
    responses={404: {"message": "Not found"}}
)


@router.get('/module_name')
async def module_index():
    return {
        'message': 'success'
    }
