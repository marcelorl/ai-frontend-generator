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

def stringify_exchange(task_exchanges, exchange_log=''):
    for i, exchange in enumerate(task_exchanges, start=1):
        if not isinstance(exchange, (list, tuple)) or len(exchange) != 2:
            return exchange_log
        prompt, result = exchange
        exchange_log += f"Task {i}:\n"
        exchange_log += f"Prompt: {prompt}\n"
        exchange_log += f"Result: {result}\n\n"
    return exchange_log

def num_tokens_from_string(string: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(string if string else ''))
    return num_tokens

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

    while True:
        # Call Orchestrator to break down the objective into the next sub-task or provide the final output
        previous_results = [result for _, result in task_exchanges]
        token_counter = num_tokens_from_string(stringify_exchange(task_exchanges))
        tokens_times = token_counter_manager(token_counter, tokens_times)

        opus_result = opus_orchestrator(objective, previous_results)

        if "The task is complete:" in opus_result:
            # If Opus indicates the task is complete, exit the loop
            break
        else:
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
    sub_tasks_results = "\n".join([result for _, result in task_exchanges])
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
    
    # WARNING: Enable this for debugging purposes
    # # Create the .md filename
    # sanitized_objective = re.sub(r'\W+', '_', objective)
    # Extract the project name from the refined output
    # project_name_match = re.search(r'Project Name: (.*)', refined_output)
    # project_name = project_name_match.group(1).strip() if project_name_match else sanitized_objective
    # timestamp = datetime.now().strftime("%H-%M-%S")
    # # Truncate the sanitized_objective to a maximum of 50 characters
    # max_length = 25
    # truncated_objective = sanitized_objective[:max_length] if len(sanitized_objective) > max_length else sanitized_objective

    # # Update the filename to include the project name
    # filename = f"../results/{timestamp}_{truncated_objective}.md"

    # # Prepare the full exchange log
    # exchange_log = f"Objective: {objective}\n\n"
    # exchange_log += "=" * 40 + " Task Breakdown " + "=" * 40 + "\n\n"
    # exchange_log = stringify_exchange(task_exchanges, exchange_log)

    # exchange_log += "=" * 40 + " Refined Final Output " + "=" * 40 + "\n\n"
    # exchange_log += refined_output

    # console.print(f"\n[bold]Refined Final output:[/bold]\n{refined_output}")

    # with open(filename, 'w') as file:
    #     file.write(exchange_log)
    # print(f"\nFull exchange log saved to {filename}")

    return files

