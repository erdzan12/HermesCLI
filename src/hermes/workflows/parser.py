import yaml
from typing import Dict, Any, List

from hermes.chat_models.base import ChatModel
from .tasks.base import Task
from .tasks.llm_task import LLMTask
from .tasks.shell_task import ShellTask
from .tasks.markdown_extraction_task import MarkdownExtractionTask
from .tasks.map_task import MapTask
from .tasks.if_else_task import IfElseTask

class WorkflowParser:
    def __init__(self, model: ChatModel):
        self.model = model

    def parse(self, workflow_file: str) -> Dict[str, Any]:
        """
        Parse a YAML workflow file and return a dictionary representation.

        Args:
            workflow_file (str): Path to the YAML workflow file.

        Returns:
            Dict[str, Any]: Parsed workflow as a dictionary.

        Raises:
            FileNotFoundError: If the workflow file doesn't exist.
            yaml.YAMLError: If there's an error parsing the YAML file.
        """
        try:
            with open(workflow_file, 'r') as file:
                workflow = yaml.safe_load(file)
            
            if self.validate_workflow(workflow):
                parsed_tasks = {}
                for task_id, task_config in workflow.get('tasks', {}).items():
                    parsed_tasks[task_id] = self.parse_task(task_id, task_config)
                workflow['tasks'] = parsed_tasks
                return workflow
            else:
                raise ValueError("Invalid workflow structure")
        except FileNotFoundError:
            raise FileNotFoundError(f"Workflow file not found: {workflow_file}")
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing workflow YAML: {e}")

    def validate_workflow(self, workflow: Dict[str, Any]) -> bool:
        """
        Validate the structure of a parsed workflow.

        Args:
            workflow (Dict[str, Any]): Parsed workflow dictionary.

        Returns:
            bool: True if the workflow is valid, False otherwise.
        """
        if 'tasks' not in workflow or not isinstance(workflow['tasks'], dict):
            return False
        for task_id, task_config in workflow['tasks'].items():
            if 'type' not in task_config:
                return False
        return True

    def parse_task(self, task_id: str, task_config: Dict[str, Any]) -> Task:
        """
        Parse a single task configuration and return the appropriate Task object.

        Args:
            task_id (str): The ID of the task.
            task_config (Dict[str, Any]): The configuration for the task.

        Returns:
            Task: An instance of the appropriate Task subclass.

        Raises:
            ValueError: If an unknown task type is encountered.
        """
        task_type = task_config.get('type')
        if task_type == 'llm':
            return LLMTask(task_id, task_config, self.model)
        elif task_type == 'shell':
            return ShellTask(task_id, task_config)
        elif task_type == 'markdown_extract':
            return MarkdownExtractionTask(task_id, task_config)
        elif task_type == 'map':
            sub_task = self.parse_task(f"{task_id}_sub", task_config['task'])
            return MapTask(task_id, task_config, sub_task)
        elif task_type == 'if_else':
            if_task = self.parse_task(f"{task_id}_if", task_config['if_task'])
            else_task = None
            if 'else_task' in task_config:
                else_task = self.parse_task(f"{task_id}_else", task_config['else_task'])
            return IfElseTask(task_id, task_config, if_task, else_task)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
