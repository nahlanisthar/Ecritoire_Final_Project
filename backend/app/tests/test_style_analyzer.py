from services.ai.style_analyzer import style_analyzer

def test_emotion_detection_finds_joy():
    text = "I am very happy and excited today! Life is wonderful."
    analysis = style_analyzer.analyze_writing_sample(text)
    emos = analysis["emotional_language"]
    assert "joy" in emos and len(emos["joy"]) >= 1

def test_formality_score_higher_with_formal_markers():
    informal = "I'm kinda okay, not too fancy."
    formal = "However, the situation is therefore considerably improved."
    ai = style_analyzer.analyze_writing_sample(informal)
    af = style_analyzer.analyze_writing_sample(formal)
    assert af["formality_score"] > ai["formality_score"]

def test_build_user_style_profile_basic_aggregation():
    s1 = style_analyzer.analyze_writing_sample("Happy times. Great vibes.")
    s2 = style_analyzer.analyze_writing_sample("However, this remains problematic.")
    profile = style_analyzer.build_user_style_profile([s1, s2])
    assert profile["sample_count"] == 2

    for key in [
        "avg_sentence_length", "formality_preference", "vocabulary_level",
        "emotional_expression_patterns", "preferred_words", "preferred_phrases",
        "punctuation_style", "style_embedding"
    ]:
        assert key in profile
