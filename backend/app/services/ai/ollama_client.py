import requests
import json
import logging

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        
    def generate_text(self, prompt: str, model: str = "llama2:3b-chat", 
                 max_tokens: int = 1000, temperature: float = 0.7) -> str:
   
        try:
            # Checking if Ollama is available
            if not self._is_ollama_available():
                return self._fallback_generation(prompt)

            payload = {
                "model": model,
                "prompt": prompt,
                "stream": True, 
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }

            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                stream=True,
                timeout=120
            )

            if response.status_code == 200:
                output = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode("utf-8"))
                            if "response" in data:
                                output += data["response"]
                            if data.get("done", False):
                                break 
                        except json.JSONDecodeError:
                            continue
                return output.strip()
            elif response.status_code == 500 and "requires more system memory" in response.text:
                logger.warning(f"{model} too large for system, trying smaller model...")
                # fallback to smaller model
                return self.generate_text(prompt, model="llama2:3b-chat", max_tokens=max_tokens, temperature=temperature)
        
            else:
                logger.warning(f"Ollama API returned status {response.status_code}: {response.text}")
                return self._fallback_generation(prompt)

        except requests.exceptions.RequestException as e:
            logger.warning(f"Ollama connection failed: {e}")
            return self._fallback_generation(prompt)
        except Exception as e:
            logger.error(f"Unexpected error in Ollama client: {e}")
            return self._fallback_generation(prompt)
    
    def _is_ollama_available(self) -> bool:
        # Checking if Ollama service is available
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _fallback_generation(self, prompt: str) -> str:
        # Fallback text generation when Ollama is not available
        prompt_lower = prompt.lower()
        
        if "email" in prompt_lower:
            return f"""Subject: Re: Your Request

        Dear [Recipient],

        Thank you for reaching out. I wanted to follow up on your message regarding the topic you mentioned.

        I'll be happy to help with this matter and will get back to you with more details soon.

        Best regards,
        [Your Name]"""
        
        elif "essay" in prompt_lower or "write about" in prompt_lower:
            return f"""Introduction

        The topic you've raised is indeed worth exploring in depth. There are several important aspects to consider when examining this subject.

        Main Points

        First, we should acknowledge the complexity of the issue. The various factors involved create a multifaceted situation that requires careful analysis.

        Furthermore, the implications extend beyond the immediate scope, affecting related areas that deserve attention.

        Conclusion

        In summary, this topic presents both challenges and opportunities. A thoughtful approach will yield the best outcomes for all involved parties."""
        
        elif "story" in prompt_lower or "creative" in prompt_lower:
            return f"""It was a day like any other, until everything changed. The morning sun streamed through the windows, casting long shadows across the room.

        As I sat there, contemplating the prompt you've given me, I realized that every story begins with a single moment of inspiration. This moment, right now, could be the beginning of something extraordinary.

        The characters in this tale are not yet fully formed, but they're waiting in the wings, ready to spring to life with the right combination of words and imagination."""
        
        else:
            return f"""Thank you for your prompt. I understand you're looking for assistance with writing content.

        Based on your request, here are some thoughts that might help guide your writing:

        Consider your audience and what they need to know. Structure your ideas in a logical flow that builds understanding step by step. Use clear, engaging language that matches your personal style.

        Remember that good writing often comes from revision and refinement, so don't worry about getting everything perfect in the first draft."""

    def __call__(self, model: str, prompt: str, **kwargs) -> str:
        """Make the client callable for backwards compatibility"""
        return self.generate_text(prompt, model, **kwargs)

ollama_client = OllamaClient()