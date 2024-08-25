from typing import Dict, Any, List, Callable
from .parser import WorkflowParser
from .context import WorkflowContext
from .tasks.base import Task
from ..chat_models.base import ChatModel
from ..prompt_formatters.base import PromptFormatter

class WorkflowExecutor:
    def __init__(self, workflow_file: str, model: ChatModel, prompt_formatter: PromptFormatter, input_files: List[str], initial_prompt: str, printer: Callable[[str], None]):
        self.model = model
        self.printer = printer
        self.parser = WorkflowParser(self.model, self.printer)
        self.context = WorkflowContext()
        self.prompt_formatter = prompt_formatter
        self.root_task: Task = self.parser.parse(workflow_file)

        # Set initial global context
        self.context.set_global('input_files', input_files)
        self.context.set_global('initial_prompt', initial_prompt)
        self.context.set_global('prompt_formatter', prompt_formatter)

    def execute(self) -> Dict[str, Any]:
        """Execute the workflow and return the final context."""
        self.model.initialize()

        result = self.root_task.execute(self.context)
        self.context.task_contexts[self.root_task.task_id] = result

        return result
