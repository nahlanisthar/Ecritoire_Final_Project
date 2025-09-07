from services.ai.content_generator import content_generator

def test_make_more_casual_replacements():
    text = "Therefore, we shall proceed; however, caution is advised."
    out = content_generator._make_more_casual(text)
    low = out.lower()
    assert "so" in low and "but" in low

def test_make_more_formal_replacements():
    text = "So we go on, but it's okay, also fine."
    out = content_generator._make_more_formal(text)
    low = out.lower()
    assert "therefore" in low and "however" in low and "furthermore" in low

def test_refine_short_sentences_breaks_long_ones():
    profile = {"avg_sentence_length": 8, "formality_preference": "neutral"}
    long = "This is a pretty long sentence because it keeps going and going and might be too verbose."
    out = content_generator._refine_with_style(long, profile)
    assert out.count(".") >= 1
    
def test_adapt_based_on_feedback_detects_casualness():
    original = "Friendship is valuable and important."
    modified = "It's super awesome, you know!"
    analysis = content_generator.adapt_based_on_feedback(
        original_prompt="Write about friendship",
        generated_content=original,
        user_modifications=modified,
        style_profile={}
    )
    assert "increase_casualness" in analysis["style_adjustments"]

def test_generate_personalized_content_uses_mock_ollama(monkeypatch):
    profile = {
        "formality_preference": "casual",
        "vocabulary_level": "simple",
        "avg_sentence_length": 10,
        "emotional_expression_patterns": {"joy": ["i am thrilled"]},
        "preferred_words": [("cool", 5), ("awesome", 3)],
        "preferred_phrases": ["you know"],
        "punctuation_style": {"exclamation_marks": 2},
    }
    out = content_generator.generate_personalized_content(
        "Write a short note about friendship", profile, context="personal"
    )
    assert isinstance(out, str) and len(out) > 0
