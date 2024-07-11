import re
from rich.console import Console
from rich.panel import Panel
from datetime import datetime
import json
from agent import opus_orchestrator, haiku_sub_agent, opus_refine
from files import create_folder_structure
import tiktoken
import time

console = Console()


# stringifying task_exchanges so I can calculate how many tokens the exchange has
def stringify_exchange(task_exchanges, exchange_log=''):
    for i, exchange in enumerate(task_exchanges, start=1):
        if not isinstance(exchange, (list, tuple)) or len(exchange) != 2:
            return exchange_log
        prompt, result = exchange
        exchange_log += f"Task {i}:\n"
        exchange_log += f"Prompt: {prompt}\n"
        exchange_log += f"Result: {result}\n\n"
    return exchange_log

# token counter
def num_tokens_from_string(string: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(string if string else ''))
    return num_tokens

# tokens_times get incremented as it gets called again, it means the prompt is getting too long, so it needs to wait 1 minute each 4k tokens computed (groq mixtral requirement)
def token_counter_manager(token_counter, tokens_times):
    if (token_counter > 4000 * tokens_times):
        console.print(Panel(f'Prompt has more than {4000 * tokens_times} tokens, waiting 1 minute'))
        tokens_times += 1
        time.sleep(70)
    return tokens_times

def run_maestro(objective):
    task_exchanges = []
    haiku_tasks = []
    tokens_times = 1
    final_exchange = []

    # looping through the prompt and incrementing it as needed
    while True:
        # Call Orchestrator to break down the objective into the next sub-task or provide the final output
        previous_results = [result for _, result in task_exchanges]
        # counting the number of tokens and waiting if needed
        token_counter = num_tokens_from_string(stringify_exchange(task_exchanges))
        tokens_times = token_counter_manager(token_counter, tokens_times)

        # it orchestrates the prompts by generating the first sub-tasks and reviewing the code generated. It also understands if all sub-tasks were applied, if so it terminates the looping
        opus_result = opus_orchestrator(objective, previous_results)

        if "The task is complete:" in opus_result:
            # If Opus indicates the task is complete, exit the loop and save as the final_exchange so it can be refined
            final_exchange.append((previous_results, opus_result))
            break
        else:
            # sub-tasks not yet completed
            sub_task_prompt = opus_result
            token_counter = num_tokens_from_string(stringify_exchange(task_exchanges, opus_result))
            tokens_times = token_counter_manager(token_counter, tokens_times)
            
            # Call haiku_sub_agent with the prepared prompt and record the result
            sub_task_result = haiku_sub_agent(sub_task_prompt, haiku_tasks)
            # Log the task and its result for future reference
            haiku_tasks.append({"task": sub_task_prompt, "result": sub_task_result})
            # Record the exchange for processing and output generation
            task_exchanges.append((sub_task_prompt, sub_task_result))

    # Call Opus to review and refine the sub-task results
    sub_tasks_results = "\n".join([result for _, result in final_exchange])
    token_counter = num_tokens_from_string(stringify_exchange(sub_tasks_results))
    token_counter_manager(token_counter, tokens_times)
    
    refined_output = opus_refine(objective, sub_tasks_results)

    # Extract the folder structure from the refined output
    folder_structure_match = re.search(r'<folder_structure>(.*?)</folder_structure>', refined_output, re.DOTALL)
    folder_structure = {}
    if folder_structure_match:
        json_string = folder_structure_match.group(1).strip()
        try:
            folder_structure = json.loads(json_string)
        except json.JSONDecodeError as e:
            console.print(Panel(f"Error parsing JSON: {e}", title="[bold red]JSON Parsing Error[/bold red]", title_align="left", border_style="red"))
            console.print(Panel(f"Invalid JSON string: [bold]{json_string}[/bold]", title="[bold red]Invalid JSON String[/bold red]", title_align="left", border_style="red"))

    # Extract code files from the refined output
    code_blocks = re.findall(r'[^\w\n]*Filename:[^\w\n]*(\S+)\s*```[\w]*\n([\s\S]*?)\n```', refined_output, re.DOTALL)
    
    # Create the folder structure and code files
    files = create_folder_structure('../results/', folder_structure, code_blocks, [])

    return files

