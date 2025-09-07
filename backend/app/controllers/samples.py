from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from models.database import get_db
from models.user import WritingSample, UserStyleProfile, User
from services.ai.style_analyzer import style_analyzer
from datetime import datetime
from controllers.auth import get_current_user

router = APIRouter(prefix="/api/samples", tags=["samples"])

class WritingSampleRequest(BaseModel):
    title: str
    content: str

class WritingSampleResponse(BaseModel):
    id: int
    title: str
    content: str
    uploaded_at: datetime
    analyzed: bool

class StyleProfileResponse(BaseModel):
    user_id: int
    sample_count: int
    vocabulary_level: str
    formality_preference: str
    avg_sentence_length: float
    emotional_patterns: dict
    created_at: datetime
    updated_at: datetime

@router.post("/upload", response_model=WritingSampleResponse)
async def upload_writing_sample(
    sample: WritingSampleRequest, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Uploading a writing sample for analysis
    if len(sample.content.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Writing sample must be at least 50 characters long"
        )

    # Creating new writing sample using current user's ID
    db_sample = WritingSample(
        user_id=current_user.id,
        title=sample.title,
        content=sample.content,
        analyzed=False
    )

    db.add(db_sample)
    db.commit()
    db.refresh(db_sample)

    return WritingSampleResponse(
        id=db_sample.id,
        title=db_sample.title,
        content=db_sample.content,
        uploaded_at=db_sample.uploaded_at,
        analyzed=db_sample.analyzed
    )

@router.post("/analyze")
async def analyze_user_samples(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Analyzing all user samples and build/update style profile
    
    samples = db.query(WritingSample).filter(WritingSample.user_id == current_user.id).all()

    if len(samples) < 1:
        raise HTTPException(
            status_code=400,
            detail="Need at least 1 writing sample to build style profile"
        )

    try:
        # Analyze each sample
        sample_analyses = []
        for sample in samples:
            analysis = style_analyzer.analyze_writing_sample(sample.content)
            sample_analyses.append(analysis)
            
            sample.analyzed = True

        # Building comprehensive style profile
        style_profile = style_analyzer.build_user_style_profile(sample_analyses)

        existing_profile = db.query(UserStyleProfile).filter(
            UserStyleProfile.user_id == current_user.id
        ).first()

        if existing_profile:
            # Updating existing profile
            existing_profile.vocabulary_level = style_profile['vocabulary_level']
            existing_profile.formality_preference = style_profile['formality_preference']
            existing_profile.sentence_complexity = style_profile['avg_sentence_length']
            existing_profile.emotional_patterns = style_profile['emotional_expression_patterns']
            existing_profile.word_preferences = {
                'words': style_profile['preferred_words'],
                'phrases': style_profile['preferred_phrases']
            }
            existing_profile.style_embedding = style_profile['style_embedding']
            existing_profile.updated_at = datetime.utcnow()
        else:
            # Creating new profile
            new_profile = UserStyleProfile(
                user_id=current_user.id,
                vocabulary_level=style_profile['vocabulary_level'],
                formality_preference=style_profile['formality_preference'],
                sentence_complexity=style_profile['avg_sentence_length'],
                emotional_patterns=style_profile['emotional_expression_patterns'],
                word_preferences={
                    'words': style_profile['preferred_words'],
                    'phrases': style_profile['preferred_phrases']
                },
                style_embedding=style_profile['style_embedding']
            )
            db.add(new_profile)

        db.commit()

        return {
            "success": True,
            "message": f"Analyzed {len(samples)} writing samples and updated style profile",
            "style_profile": {
                "vocabulary_level": style_profile['vocabulary_level'],
                "formality_preference": style_profile['formality_preference'],
                "avg_sentence_length": round(style_profile['avg_sentence_length'], 2),
                "sample_count": len(samples),
                "emotional_patterns": len(style_profile['emotional_expression_patterns'])
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )

@router.get("/user", response_model=List[WritingSampleResponse])
async def get_user_samples(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    samples = db.query(WritingSample).filter(WritingSample.user_id == current_user.id).all()

    return [
        WritingSampleResponse(
            id=sample.id,
            title=sample.title,
            content=sample.content,
            uploaded_at=sample.uploaded_at,
            analyzed=sample.analyzed
        )
        for sample in samples
    ]

@router.get("/profile")
async def get_user_style_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(UserStyleProfile).filter(
        UserStyleProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Style profile not found. Please upload and analyze writing samples first."
        )

    return {
        "user_id": profile.user_id,
        "vocabulary_level": profile.vocabulary_level,
        "formality_preference": profile.formality_preference,
        "sentence_complexity": profile.sentence_complexity,
        "sample_count": len(profile.emotional_patterns) if profile.emotional_patterns else 0,
        "emotional_patterns": profile.emotional_patterns,
        "word_preferences": profile.word_preferences,
        "created_at": profile.created_at,
        "updated_at": profile.updated_at
    }

@router.delete("/sample/{sample_id}")
async def delete_writing_sample(
    sample_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Delete a writing sample
    sample = db.query(WritingSample).filter(
        WritingSample.id == sample_id,
        WritingSample.user_id == current_user.id  # Ensure user owns this sample
    ).first()

    if not sample:
        raise HTTPException(status_code=404, detail="Writing sample not found")

    db.delete(sample)
    db.commit()

    return {"success": True, "message": "Writing sample deleted successfully"}