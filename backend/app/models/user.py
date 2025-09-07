from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, JSON
from sqlalchemy.sql import func
from models.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)

class WritingSample(Base):
    __tablename__ = "writing_samples"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    uploaded_at = Column(DateTime, default=func.now())
    analyzed = Column(Boolean, default=False)

class UserStyleProfile(Base):
    __tablename__ = "user_style_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, nullable=False)
    vocabulary_level = Column(String) 
    formality_preference = Column(String) 
    sentence_complexity = Column(Float)  
    emotional_patterns = Column(JSON) 
    word_preferences = Column(JSON)  
    style_embedding = Column(JSON)  
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class GeneratedContent(Base):
    __tablename__ = "generated_content"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    prompt = Column(Text, nullable=False)
    generated_text = Column(Text, nullable=False)
    user_feedback = Column(String)  
    user_modifications = Column(Text)  
    created_at = Column(DateTime, default=func.now())

class FeedbackHistory(Base):
    __tablename__ = "feedback_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    content_id = Column(Integer, nullable=False)
    feedback_type = Column(String)
    original_text = Column(Text)
    modified_text = Column(Text)
    timestamp = Column(DateTime, default=func.now())
    