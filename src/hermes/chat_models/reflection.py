from typing import Generator
from .openai import OpenAIModel

class ReflectionModel(OpenAIModel):
    def initialize(self):
        self.config = dict(self.config)
        self.config["OPENAI"] = {
            "api_key": self.config["REFLECTION"]["api_key"],
            "base_url": "https://openrouter.ai/api/v1",
            "model": self.config["REFLECTION"].get("model", "mattshumer/reflection-70b"),
        }
        super().initialize()
        super().add_system_message("You are a world-class AI system, capable of complex reasoning and reflection. Reason through the query inside <thinking> tags, and then provide your final response inside <output> tags. If you detect that you made a mistake in your reasoning at any point, correct yourself inside <reflection> tags.")

    def send_message(self, message: str) -> Generator[str, None, None]:
        return super().send_message(message)
