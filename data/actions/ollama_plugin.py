# data/actions/ollama_plugin.py
from plugin_base import PluginBase
import ollama
from logger import LoggerFactory

class OllamaPlugin(PluginBase):
    def __init__(self, context, debug=False):
        super().__init__(context, debug)
        self.logger.debug("Initializing OllamaPlugin")
        self.register_action('ollama_chat', self.ollama_chat)
    
    def ollama_chat(self, prompt, model=None, **kwargs):
        """
        Makes a chat request to the Ollama API.

        Args:
            prompt (str): The prompt text to send to the model.
            model (str): The model name. If not provided, it will use the model from the DI layer.

        Returns:
            str: The response from the model.
        """
        self.logger.debug(f"Preparing to call Ollama API with model: {model or 'default'}")
        
        # Retrieve the model from the DI layer if not provided
        if not model:
            model = self.di_layer.get('model')
        
        self.logger.debug(f"Using model: {model}")

        try:
            # Perform the Ollama chat call
            response = ollama.chat(model=model, messages=[
                {
                    'role': 'user',
                    'content': prompt,
                },
            ])
            answer = response['message']['content']
            self.logger.debug(f"Ollama API response: {answer[:100]}...")
        except Exception as e:
            self.logger.error(f"Ollama API call failed: {e}")

        # Optionally store the answer in the DI layer
        self.di_layer.set('answer', answer)
        return answer
