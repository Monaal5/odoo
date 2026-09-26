from fastapi import APIRouter, Depends, HTTPException, status
from app.db.database import get_db
from app.schemas.ai_chat import AIChatRequest, AIChatResponse
from app.services.ai_service import AIService
from app.api.deps import get_current_user

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


@router.post("/chat", response_model=AIChatResponse)
def ai_chat(
    body: AIChatRequest,
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    AI Warehouse Assistant endpoint.
    Processes natural-language queries about stock levels, locations, low stock alerts, and pending work.

    Example Request:
    ```json
    {
      "query": "How much steel is in Rack B?"
    }
    ```

    Example Response:
    ```json
    {
      "answer": "Rack B currently contains 42 Steel Rods."
    }
    ```
    """
    try:
        return AIService.process_query(conn, body.query)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI Chat error: {str(e)}",
        )
