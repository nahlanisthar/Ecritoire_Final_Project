import re
import json
import math
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Any
import numpy as np

class StyleAnalyzer:
    def __init__(self):
        # Common English stop words
        self.stop_words = set([
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'were', 'will', 'with', 'she', 'her', 'his', 'him',
            'they', 'them', 'their', 'we', 'us', 'our', 'you', 'your', 'i',
            'me', 'my', 'this', 'these', 'those', 'there', 'where', 'when',
            'what', 'why', 'how', 'can', 'could', 'would', 'should', 'may',
            'might', 'must', 'shall', 'do', 'does', 'did', 'have', 'had'
        ])
        
        # Emotion word dictionaries
        self.emotion_words = {
            'joy': ['happy', 'excited', 'thrilled', 'delighted', 'cheerful', 'elated', 'joyful', 'ecstatic'],
            'sadness': ['sad', 'depressed', 'melancholy', 'gloomy', 'sorrowful', 'heartbroken', 'dejected'],
            'anger': ['angry', 'furious', 'irritated', 'annoyed', 'rage', 'mad', 'outraged', 'livid'],
            'fear': ['scared', 'afraid', 'terrified', 'anxious', 'worried', 'nervous', 'frightened'],
            'love': ['love', 'adore', 'cherish', 'treasure', 'devoted', 'affectionate', 'fond'],
            'surprise': ['surprised', 'shocked', 'amazed', 'astonished', 'stunned', 'bewildered']
        }
        
        # Formal vs informal indicators
        self.formal_words = [
            'therefore', 'furthermore', 'consequently', 'moreover', 'nevertheless',
            'however', 'indeed', 'thus', 'hence', 'accordingly', 'subsequently'
        ]
        
        self.informal_words = [
            "i'm", "don't", "can't", "won't", "isn't", "aren't", "wasn't", "weren't",
            'gonna', 'wanna', 'gotta', 'yeah', 'ok', 'okay', 'totally', 'really'
        ]

    def analyze_writing_sample(self, text: str) -> Dict:
        """Comprehensive analysis of a single writing sample"""
        
        # Cleaning and prepare text
        clean_text = self._clean_text(text)
        words = clean_text.split()
        sentences = self._split_into_sentences(text)
        
        # Basic metrics
        word_count = len(words)
        sentence_count = len(sentences)
        avg_sentence_length = word_count / max(sentence_count, 1)
        avg_word_length = sum(len(word) for word in words) / max(word_count, 1)
        
        # Vocabulary analysis
        unique_words = set(word.lower() for word in words if word.isalpha())
        vocabulary_richness = len(unique_words) / max(word_count, 1)
        
        # Readability
        flesch_score = self._calculate_flesch_score(text, words, sentences)
        grade_level = self._calculate_grade_level(flesch_score)
        
        analysis = {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_sentence_length': avg_sentence_length,
            'avg_word_length': avg_word_length,

            'flesch_reading_ease': flesch_score,
            'flesch_kincaid_grade': grade_level,
            
            'unique_words': len(unique_words),
            'vocabulary_richness': vocabulary_richness,

            'sentence_structures': self._analyze_sentence_structures(sentences),

            'punctuation_usage': self._analyze_punctuation(text),

            'emotional_language': self._analyze_emotional_language(text.lower()),

            'formality_score': self._calculate_formality(text.lower()),
            
            'frequent_words': self._get_frequent_words(words),
            'frequent_phrases': self._get_frequent_phrases(text),

            'pos_patterns': self._analyze_pos_patterns_simple(words),

            'sentiment': self._analyze_sentiment_simple(text.lower()),

            'style_embedding': self._get_style_embedding_simple(text, words, sentences)
        }
        
        return analysis

    def _clean_text(self, text: str) -> str:
        # Removing extra whitespace and normalizing
        text = re.sub(r'\s+', ' ', text.strip())
        return text

    def _split_into_sentences(self, text: str) -> List[str]:
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences

    def _calculate_flesch_score(self, text: str, words: List[str], sentences: List[str]) -> float:
        if not words or not sentences:
            return 50.0  # neutral score
        
        # Counting syllables
        total_syllables = sum(self._count_syllables(word) for word in words)
        
        avg_sentence_length = len(words) / len(sentences)
        avg_syllables_per_word = total_syllables / len(words)
        
        score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        return max(0, min(100, score))

    def _count_syllables(self, word: str) -> int:
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
        
        # Handle silent e
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
            
        return max(1, syllable_count)

    def _calculate_grade_level(self, flesch_score: float) -> float:
        if flesch_score >= 90:
            return 5.0
        elif flesch_score >= 80:
            return 6.0
        elif flesch_score >= 70:
            return 7.0
        elif flesch_score >= 60:
            return 8.5
        elif flesch_score >= 50:
            return 10.0
        elif flesch_score >= 30:
            return 13.0
        else:
            return 16.0

    def _analyze_sentence_structures(self, sentences: List[str]) -> Dict:
        structures = {
            'simple': 0,
            'compound': 0,
            'complex': 0,
            'avg_clauses_per_sentence': 0
        }
        
        total_clauses = 0
        for sentence in sentences:
            # Counting conjunctions as indicator of complexity
            conjunctions = len(re.findall(r'\b(and|but|or|so|yet|for|nor|because|although|since|while|if|unless|when|where|after|before)\b', sentence.lower()))
            clauses = max(1, conjunctions + 1)
            total_clauses += clauses
            
            if clauses == 1:
                structures['simple'] += 1
            elif 'and' in sentence.lower() or 'but' in sentence.lower() or 'or' in sentence.lower():
                structures['compound'] += 1
            else:
                structures['complex'] += 1
        
        structures['avg_clauses_per_sentence'] = total_clauses / max(len(sentences), 1)
        return structures

    def _analyze_punctuation(self, text: str) -> Dict:
        return {
            'exclamation_marks': text.count('!'),
            'question_marks': text.count('?'),
            'ellipsis': text.count('...'),
            'semicolons': text.count(';'),
            'colons': text.count(':'),
            'dashes': text.count('---') + text.count('--'),
            'parentheses': text.count('('),
            'quotation_marks': text.count('"') + text.count("'")
        }

    def _analyze_emotional_language(self, text_lower: str) -> Dict:
        emotions_found = defaultdict(list)
        
        for emotion, words in self.emotion_words.items():
            for word in words:
                if word in text_lower:
                    # Find context around the emotion word
                    pattern = rf'.{{0,20}}\b{re.escape(word)}\b.{{0,20}}'
                    matches = re.findall(pattern, text_lower)
                    emotions_found[emotion].extend(matches)
        
        return dict(emotions_found)

    def _calculate_formality(self, text_lower: str) -> float:
        formal_count = sum(1 for word in self.formal_words if word in text_lower)
        informal_count = sum(1 for word in self.informal_words if word in text_lower)
        
        if formal_count + informal_count == 0:
            return 0.5  # neutral
        
        return formal_count / (formal_count + informal_count)

    def _get_frequent_words(self, words: List[str], top_n: int = 20) -> List[Tuple[str, int]]:
        # Getting most frequently used words (excluding stop words)
        filtered_words = [
            word.lower() for word in words 
            if word.isalpha() and word.lower() not in self.stop_words and len(word) > 2
        ]
        return Counter(filtered_words).most_common(top_n)

    def _get_frequent_phrases(self, text: str, top_n: int = 10) -> List[Tuple[str, int]]:
        #Getting most frequently used phrases
        words = re.findall(r'\b\w+\b', text.lower())
        bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
        trigrams = [f"{words[i]} {words[i+1]} {words[i+2]}" for i in range(len(words)-2)]
        
        all_phrases = bigrams + trigrams
        return Counter(all_phrases).most_common(top_n)

    def _analyze_pos_patterns_simple(self, words: List[str]) -> Dict:
        adjectives = sum(1 for word in words if word.lower().endswith(('ly', 'ful', 'less', 'able', 'ible')))
        
        return {
            'adjective_ratio': adjectives / max(len(words), 1),
            'adverb_ratio': sum(1 for word in words if word.lower().endswith('ly')) / max(len(words), 1),
            'estimated_complexity': len(set(word.lower() for word in words if len(word) > 6)) / max(len(words), 1)
        }

    def _analyze_sentiment_simple(self, text_lower: str) -> Dict:
        # sentiment analysis
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'like', 'enjoy', 'happy', 'pleased']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike', 'sad', 'angry', 'disappointed', 'upset']
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        total_sentiment_words = pos_count + neg_count
        
        if total_sentiment_words == 0:
            polarity = 0.0
        else:
            polarity = (pos_count - neg_count) / total_sentiment_words
        
        subjectivity = min(1.0, total_sentiment_words / 100)  # Rough estimate
        
        return {
            'polarity': polarity,
            'subjectivity': subjectivity
        }

    def _get_style_embedding_simple(self, text: str, words: List[str], sentences: List[str]) -> List[float]:
        # Creating a basic feature vector representing writing style
        features = [
            len(words) / 1000,  # Normalized word count
            len(sentences) / 100,  # Normalized sentence count
            len(words) / max(len(sentences), 1) / 20,  # Normalized avg sentence length
            sum(len(word) for word in words) / max(len(words), 1) / 10,  # Normalized avg word length
            text.count('!') / 10,  # Normalized exclamation usage
            text.count('?') / 10,  # Normalized question usage
            self._calculate_formality(text.lower()),  # Formality score
            len(set(word.lower() for word in words)) / max(len(words), 1),  # Vocabulary richness
        ]
        
        while len(features) < 32:
            features.append(0.0)
        features = features[:32]
        
        return features

    def build_user_style_profile(self, sample_analyses: List[Dict]) -> Dict:
        if not sample_analyses:
            return {}

        profile = {
            'sample_count': len(sample_analyses),
            'avg_sentence_length': float(np.mean([s['avg_sentence_length'] for s in sample_analyses])),
            'avg_word_length': float(np.mean([s['avg_word_length'] for s in sample_analyses])),
            'vocabulary_richness': float(np.mean([s['vocabulary_richness'] for s in sample_analyses])),
            'avg_readability': float(np.mean([s['flesch_reading_ease'] for s in sample_analyses])),
            'grade_level': float(np.mean([s['flesch_kincaid_grade'] for s in sample_analyses])),
            'formality_preference': self._determine_formality_preference(sample_analyses),
            'vocabulary_level': self._determine_vocabulary_level(sample_analyses),
            'emotional_expression_patterns': self._build_emotional_patterns(sample_analyses),
            'sentence_structure_preference': self._determine_structure_preference(sample_analyses),
            'preferred_words': self._get_overall_word_preferences(sample_analyses),
            'preferred_phrases': self._get_overall_phrase_preferences(sample_analyses),
            'punctuation_style': self._determine_punctuation_style(sample_analyses),
            'sentiment_tendencies': self._determine_sentiment_tendencies(sample_analyses),
            'style_embedding': self._create_average_embedding(sample_analyses)
        }

        return profile

    def _determine_formality_preference(self, analyses: List[Dict]) -> str:
        # Determining user's formality preference
        avg_formality = np.mean([a['formality_score'] for a in analyses])
        
        if avg_formality > 0.7:
            return 'formal'
        elif avg_formality < 0.4:
            return 'casual'
        else:
            return 'neutral'

    def _determine_vocabulary_level(self, analyses: List[Dict]) -> str:
        # Determine user's vocabulary complexity level
        avg_grade_level = np.mean([a['flesch_kincaid_grade'] for a in analyses])
        
        if avg_grade_level > 12:
            return 'advanced'
        elif avg_grade_level > 8:
            return 'intermediate'
        else:
            return 'simple'

    def _build_emotional_patterns(self, analyses: List[Dict]) -> Dict:
        all_emotional_language = defaultdict(list)
        
        for analysis in analyses:
            for emotion, contexts in analysis['emotional_language'].items():
                all_emotional_language[emotion].extend(contexts)
        
        return dict(all_emotional_language)

    def _determine_structure_preference(self, analyses: List[Dict]) -> Dict:
        structure_totals = defaultdict(int)
        total_sentences = 0
        
        for analysis in analyses:
            structures = analysis['sentence_structures']
            for struct_type, count in structures.items():
                if struct_type != 'avg_clauses_per_sentence':
                    structure_totals[struct_type] += count
                    total_sentences += count
        
        # Calculate percentages
        return {
            struct_type: count / max(total_sentences, 1)
            for struct_type, count in structure_totals.items()
        }

    def _get_overall_word_preferences(self, analyses: List[Dict]) -> List[Tuple[str, int]]:
        # Get overall word preferences across all samples
        all_words = Counter()
        
        for analysis in analyses:
            for word, count in analysis['frequent_words']:
                all_words[word] += count
        
        return all_words.most_common(30)

    def _get_overall_phrase_preferences(self, analyses: List[Dict]) -> List[Tuple[str, int]]:
        all_phrases = Counter()
        
        for analysis in analyses:
            for phrase, count in analysis['frequent_phrases']:
                all_phrases[phrase] += count
        
        return all_phrases.most_common(20)

    def _determine_punctuation_style(self, analyses: List[Dict]) -> Dict:
        punct_totals = defaultdict(int)
        word_count_total = 0
        
        for analysis in analyses:
            punct = analysis['punctuation_usage']
            words = analysis['word_count']
            word_count_total += words
            
            for punct_type, count in punct.items():
                punct_totals[punct_type] += count
        
        return {
            punct_type: count / max(word_count_total, 1) * 1000  # per 1000 words
            for punct_type, count in punct_totals.items()
        }

    def _determine_sentiment_tendencies(self, analyses: List[Dict]) -> Dict:
        polarities = [a['sentiment']['polarity'] for a in analyses]
        subjectivities = [a['sentiment']['subjectivity'] for a in analyses]
        
        return {
            'avg_polarity': float(np.mean(polarities)),
            'avg_subjectivity': float(np.mean(subjectivities)),
            'sentiment_consistency': float(1 - np.std(polarities))  # Lower std = more consistent
        }

    def _create_average_embedding(self, analyses: List[Dict]) -> List[float]:
        embeddings = [np.array(a['style_embedding']) for a in analyses]
        avg_embedding = np.mean(embeddings, axis=0)
        return avg_embedding.tolist()

style_analyzer = StyleAnalyzer()