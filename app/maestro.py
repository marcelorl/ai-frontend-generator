import re
from rich.console import Console
from rich.panel import Panel
import json
from agent import gpt_orchestrator, gpt_sub_agent, gpt_refine
from files import create_folder_structure

console = Console()

def run_maestro(objective):
    task_exchanges = []
    gpt_tasks = []

    # looping through the prompt and incrementing it as needed
    while True:
        # Call Orchestrator to break down the objective into the next sub-task or provide the final output
        previous_results = [result for _, result in task_exchanges]
        # it orchestrates the prompts by generating the first sub-tasks and reviewing the code generated. It also understands if all sub-tasks were applied, if so it terminates the looping
        gpt_result = gpt_orchestrator(objective, previous_results)

        if "The task is complete:" in gpt_result:
            break
        else:
            # sub-tasks not yet completed
            sub_task_prompt = gpt_result
            # Call gpt_sub_agent with the prepared prompt and record the result
            sub_task_result = gpt_sub_agent(sub_task_prompt, gpt_tasks)
            # Log the task and its result for future reference
            gpt_tasks.append({"task": sub_task_prompt, "result": sub_task_result})
            # Record the exchange for processing and output generation
            task_exchanges.append((sub_task_prompt, sub_task_result))

    # Call gpt to review and refine the sub-task results
    sub_tasks_results = "\n".join([result for _, result in task_exchanges])
    
    refined_output = gpt_refine(objective, sub_tasks_results)

    # Extract the project name from the refined output
    sanitized_objective = re.sub(r'\W+', '_', objective)
    project_name_match = re.search(r'Project Name: (.*)', refined_output)
    project_name = project_name_match.group(1).strip() if project_name_match else sanitized_objective

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
    files = create_folder_structure('../results/'+project_name, folder_structure, code_blocks, [])

    print('+++++++++++++++++++++++>', type(files))
    print('=================>', *files)

    return files

