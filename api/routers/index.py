from fastapi import APIRouter

router = APIRouter()


@router.get('/')
async def index():
    return {
        'message': 'I am the API.'
    }
