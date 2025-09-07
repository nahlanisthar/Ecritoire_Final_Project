from services.ai.ollama_client import ollama_client
from typing import Dict
import re

class ContentGenerator:
    def __init__(self):
        pass
    
    def generate_personalized_content(self, prompt: str, user_style_profile: Dict, context: str = "general") -> str:
        """Generate content matching user's personal style"""
        
        if not user_style_profile:
            return self._generate_generic_content(prompt)
        
        # Building style-aware prompt
        style_prompt = self._build_style_prompt(prompt, user_style_profile, context)
        
        # Generating content using AI
        generated = ollama_client(model="llama2:7b-chat", prompt=style_prompt)
        
        # to match user style
        refined = self._refine_with_style(generated, user_style_profile)
        
        return refined
    
    def _build_style_prompt(self, user_prompt: str, style_profile: Dict, context: str) -> str:
        
        # Extracting key style characteristics
        formality = style_profile.get('formality_preference', 'neutral')
        vocab_level = style_profile.get('vocabulary_level', 'intermediate')
        avg_sent_length = style_profile.get('avg_sentence_length', 15)
        
        # Getting emotional patterns
        emotional_patterns = style_profile.get('emotional_expression_patterns', {})
        
        # Getting preferred words
        preferred_words = [word for word, _ in style_profile.get('preferred_words', [])[:10]]
        
        # Building style description
        style_description = f"""
        Write in a {formality} style with {vocab_level} vocabulary. 
        Average sentence length should be around {avg_sent_length:.0f} words.
        """ 
        
        if preferred_words:
            style_description += f"Try to naturally incorporate words like: {', '.join(preferred_words[:5])}. "
        
        if context in ["personal", "emotional", "creative"]:
            if emotional_patterns:
                style_description += "When expressing emotions, use patterns similar to these examples: "
                for emotion, examples in list(emotional_patterns.items())[:2]:
                    if examples:
                        style_description += f"{emotion}: '{examples[0][:50]}...' "
        

        punct_style = style_profile.get('punctuation_style', {})
        exclamation_rate = punct_style.get('exclamation_marks', 0)
        if exclamation_rate > 5:  
            style_description += "Use exclamation marks to show enthusiasm. "
        elif exclamation_rate < 1:  
            style_description += "Avoid excessive exclamation marks, keep tone measured. "
        
        # Building final prompt
        final_prompt = f"""
        {style_description}

        User request: {user_prompt}

        Please respond in the writing style described above, making it sound natural and authentic:
        """
        
        return final_prompt
    
    def _generate_generic_content(self, prompt: str) -> str:
        # Generating generic content when no user style is available
        return ollama_client.generate_text(f"Please help with this request: {prompt}")
    
    def _refine_with_style(self, generated_text: str, style_profile: Dict) -> str:
        
        target_length = style_profile.get('avg_sentence_length', 15)
        
        if target_length < 12:
            generated_text = self._break_long_sentences(generated_text)
        
        elif target_length > 20:
            generated_text = self._combine_short_sentences(generated_text)
        
        # Adjusting formality 
        formality = style_profile.get('formality_preference', 'neutral')
        if formality == 'casual':
            generated_text = self._make_more_casual(generated_text)
        elif formality == 'formal':
            generated_text = self._make_more_formal(generated_text)
        
        return generated_text.strip()
    
    def _break_long_sentences(self, text: str) -> str:
        sentences = re.split(r'[.!?]', text)
        processed = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            words = sentence.split()
            if len(words) > 25:  
                # break at conjunctions
                for i, word in enumerate(words):
                    if word.lower() in ['and', 'but', 'so', 'because', 'while'] and i > 8:
                        part1 = ' '.join(words[:i])
                        part2 = ' '.join(words[i+1:])
                        processed.extend([part1, part2])
                        break
                else:
                    processed.append(sentence)
            else:
                processed.append(sentence)
        
        return '. '.join(processed) + '.'
    
    def _combine_short_sentences(self, text: str) -> str:
        """Combine sentences that are too short"""
        sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
        processed = []
        i = 0
        
        while i < len(sentences):
            current = sentences[i]
            
            if len(current.split()) < 8 and i + 1 < len(sentences):
                next_sent = sentences[i + 1]
                combined = f"{current}, and {next_sent.lower()}"
                processed.append(combined)
                i += 2
            else:
                processed.append(current)
                i += 1
        
        return '. '.join(processed) + '.'
    
    def _make_more_casual(self, text: str) -> str:
        """Make text more casual"""
        casual_replacements = {
            'therefore': 'so',
            'however': 'but',
            'furthermore': 'also',
            'consequently': 'so',
            'nevertheless': 'but still'
        }
        
        for formal, casual in casual_replacements.items():
            text = re.sub(rf'\b{formal}\b', casual, text, flags=re.IGNORECASE)
        
        return text
    
    def _make_more_formal(self, text: str) -> str:
        """Make text more formal"""
        formal_replacements = {
            r'\bso\b': 'therefore',
            r'\bbut\b': 'however',
            r'\balso\b': 'furthermore',
            r'\banyway\b': 'nonetheless'
        }
        
        for casual, formal in formal_replacements.items():
            text = re.sub(casual, formal, text, flags=re.IGNORECASE)
        
        return text
    
    def adapt_based_on_feedback(self, original_prompt: str, generated_content: str, 
                              user_modifications: str, style_profile: Dict) -> Dict:
        
        # Analyzing what the user changed
        feedback_analysis = {
            'prompt': original_prompt,
            'original_length': len(generated_content.split()),
            'modified_length': len(user_modifications.split()),
            'style_adjustments': []
        }
        
        # Detecting specific changes
        if len(user_modifications.split()) > len(generated_content.split()) * 1.2:
            feedback_analysis['style_adjustments'].append('prefers_longer_content')
        elif len(user_modifications.split()) < len(generated_content.split()) * 0.8:
            feedback_analysis['style_adjustments'].append('prefers_shorter_content')
        
        # Detecting formality changes
        if self._is_more_formal(user_modifications, generated_content):
            feedback_analysis['style_adjustments'].append('increase_formality')
        elif self._is_more_casual(user_modifications, generated_content):
            feedback_analysis['style_adjustments'].append('increase_casualness')
        
        # Detecting vocabulary changes
        if self._uses_simpler_words(user_modifications, generated_content):
            feedback_analysis['style_adjustments'].append('prefer_simpler_vocabulary')
        elif self._uses_complex_words(user_modifications, generated_content):
            feedback_analysis['style_adjustments'].append('prefer_complex_vocabulary')
        
        return feedback_analysis
    
    def _is_more_formal(self, modified: str, original: str) -> bool:
        formal_words = ['therefore', 'however', 'furthermore', 'consequently', 'moreover']
        
        original_formal = sum(1 for word in formal_words if word in original.lower())
        modified_formal = sum(1 for word in formal_words if word in modified.lower())
        
        return modified_formal > original_formal
    
    def _is_more_casual(self, modified: str, original: str) -> bool:
        casual_words = ["don't", "can't", "won't", "it's", "that's", 'gonna', 'wanna']
        
        original_casual = sum(1 for word in casual_words if word in original.lower())
        modified_casual = sum(1 for word in casual_words if word in modified.lower())
        
        return modified_casual > original_casual
    
    def _uses_simpler_words(self, modified: str, original: str) -> bool:
        return len(modified.split()) > len(original.split()) and len(modified) < len(original)
    
    def _uses_complex_words(self, modified: str, original: str) -> bool:
        return len(modified.split()) < len(original.split()) and len(modified) > len(original)

content_generator = ContentGenerator()