from typing import Any, Dict, List, Callable
from .base import Task
from ..context import WorkflowContext

class SequentialTask(Task):
    def __init__(self, task_id: str, task_config: Dict[str, Any], sub_tasks: List[Task], printer: Callable[[str], None]):
        super().__init__(task_id, task_config, printer)
        self.sub_tasks = sub_tasks
        self.task_config['output_mapping'] = {
            key: 'result.' + key for subtask in self.sub_tasks for key in subtask.get_config('output_mapping', {})
        }

    def execute(self, context: WorkflowContext) -> Dict[str, Any]:
        context = context.copy()
        results = {}
        debug_results = []
        for sub_task in self.sub_tasks:
            sub_result = sub_task.execute(context)
            results[sub_task.task_id] = sub_result
            debug_results.append({
                'task_id': sub_task.task_id,
                'result': sub_result
            })

            # Update global context with output mappings
            output_mapping = sub_task.get_config('output_mapping', {})
            for key, value in output_mapping.items():
                if isinstance(value, str) and value.startswith('result.'):
                    result_key = value.split('.', 1)[1]
                    if result_key in sub_result:
                        context.set_global(key, sub_result[result_key])
                        results[key] = sub_result[result_key]

        results['_debug'] = debug_results
        return results
