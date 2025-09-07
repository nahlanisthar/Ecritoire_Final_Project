from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from models.database import get_db
from models.user import UserStyleProfile, GeneratedContent, FeedbackHistory, User
from services.ai.content_generator import content_generator
from controllers.auth import get_current_user

router = APIRouter(prefix="/api/generate", tags=["generation"])

class ContentGenerationRequest(BaseModel):
    prompt: str
    context: Optional[str] = "general"  

class ContentGenerationResponse(BaseModel):
    success: bool
    generated_content: str
    content_id: int
    message: str

class FeedbackRequest(BaseModel):
    content_id: int
    feedback_type: str 
    modified_content: Optional[str] = None

@router.post("/content", response_model=ContentGenerationResponse)
async def generate_content(
    request: ContentGenerationRequest, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if not request.prompt or len(request.prompt.strip()) < 5:
        raise HTTPException(
            status_code=400,
            detail="Prompt must be at least 5 characters long"
        )

    try:
        # Getting current user's style profile
        style_profile = db.query(UserStyleProfile).filter(
            UserStyleProfile.user_id == current_user.id
        ).first()

        if not style_profile:
            raise HTTPException(
                status_code=404,
                detail="Style profile not found. Please upload writing samples first."
            )

        # Converting profile to dict for content generator
        profile_dict = {
            'formality_preference': style_profile.formality_preference,
            'vocabulary_level': style_profile.vocabulary_level,
            'avg_sentence_length': style_profile.sentence_complexity,
            'emotional_expression_patterns': style_profile.emotional_patterns or {},
            'preferred_words': style_profile.word_preferences.get('words', []) if style_profile.word_preferences else [],
            'preferred_phrases': style_profile.word_preferences.get('phrases', []) if style_profile.word_preferences else [],
        }

        # Generating content
        generated_text = content_generator.generate_personalized_content(
            request.prompt,
            profile_dict,
            request.context
        )

        # Saving generated content
        db_content = GeneratedContent(
            user_id=current_user.id,
            prompt=request.prompt,
            generated_text=generated_text,
            user_feedback=None
        )

        db.add(db_content)
        db.commit()
        db.refresh(db_content)

        return ContentGenerationResponse(
            success=True,
            generated_content=generated_text,
            content_id=db_content.id,
            message="Content generated successfully in your personal style"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Content generation failed: {str(e)}"
        )

@router.post("/feedback")
async def submit_feedback(
    feedback: FeedbackRequest, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    content = db.query(GeneratedContent).filter(
        GeneratedContent.id == feedback.content_id,
        GeneratedContent.user_id == current_user.id
    ).first()

    if not content:
        raise HTTPException(status_code=404, detail="Generated content not found")

    try:
        content.user_feedback = feedback.feedback_type
        if feedback.modified_content:
            content.user_modifications = feedback.modified_content

        if feedback.feedback_type == "modified" and feedback.modified_content:
            style_profile = db.query(UserStyleProfile).filter(
                UserStyleProfile.user_id == current_user.id
            ).first()

            if style_profile:
                # Analyzing feedback for learning
                profile_dict = {
                    'formality_preference': style_profile.formality_preference,
                    'vocabulary_level': style_profile.vocabulary_level,
                    'avg_sentence_length': style_profile.sentence_complexity,
                }

                feedback_analysis = content_generator.adapt_based_on_feedback(
                    content.prompt,
                    content.generated_text,
                    feedback.modified_content,
                    profile_dict
                )

        # Saving feedback for future learning
        db_feedback = FeedbackHistory(
            user_id=current_user.id,
            content_id=feedback.content_id,
            feedback_type=feedback.feedback_type,
            original_text=content.generated_text,
            modified_text=feedback.modified_content
        )

        db.add(db_feedback)
        db.commit()

        return {
            "success": True,
            "message": "Feedback submitted successfully. This will help improve future generations."
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit feedback: {str(e)}"
        )

@router.get("/history")
async def get_generation_history(
    limit: int = 20, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's content generation history"""

    history = db.query(GeneratedContent).filter(
        GeneratedContent.user_id == current_user.id
    ).order_by(GeneratedContent.created_at.desc()).limit(limit).all()

    return {
        "success": True,
        "history": [
            {
                "id": content.id,
                "prompt": content.prompt,
                "generated_text": content.generated_text,
                "user_feedback": content.user_feedback,
                "created_at": content.created_at,
                "has_modifications": bool(content.user_modifications)
            }
            for content in history
        ]
    }

@router.get("/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's generation statistics"""

    total_generations = db.query(GeneratedContent).filter(
        GeneratedContent.user_id == current_user.id
    ).count()

    accepted = db.query(GeneratedContent).filter(
        GeneratedContent.user_id == current_user.id,
        GeneratedContent.user_feedback == "accepted"
    ).count()

    modified = db.query(GeneratedContent).filter(
        GeneratedContent.user_id == current_user.id,
        GeneratedContent.user_feedback == "modified"
    ).count()

    rejected = db.query(GeneratedContent).filter(
        GeneratedContent.user_id == current_user.id,
        GeneratedContent.user_feedback == "rejected"
    ).count()

    return {
        "success": True,
        "stats": {
            "total_generations": total_generations,
            "accepted": accepted,
            "modified": modified,
            "rejected": rejected,
            "acceptance_rate": (accepted / max(total_generations, 1)) * 100,
            "modification_rate": (modified / max(total_generations, 1)) * 100
        }
    }