import re
from rich.console import Console
from rich.panel import Panel
from datetime import datetime
import json
from agent import opus_orchestrator, haiku_sub_agent, opus_refine
from files import create_folder_structure

console = Console()

def run_maestro(objective):
    # Check if the input contains a file path
    if "./" in objective or "/" in objective:
        # Extract the file path from the objective
        file_path = re.findall(r'[./\w]+\.[\w]+', objective)[0]
        # Read the file content
        with open(file_path, 'r') as file:
            file_content = file.read()
        # Update the objective string to remove the file path
        objective = objective.split(file_path)[0].strip()
    else:
        file_content = None

    task_exchanges = []
    haiku_tasks = []

    while True:
        # Call Orchestrator to break down the objective into the next sub-task or provide the final output
        previous_results = [result for _, result in task_exchanges]
        if not task_exchanges:
            # Pass the file content only in the first iteration if available
            opus_result, file_content_for_haiku = opus_orchestrator(objective, file_content, previous_results)
        else:
            opus_result, _ = opus_orchestrator(objective, previous_results=previous_results)

        if "The task is complete:" in opus_result:
            # If Opus indicates the task is complete, exit the loop
            final_output = opus_result.replace("The task is complete:", "").strip()
            break
        else:
            sub_task_prompt = opus_result
            # Append file content to the prompt for the initial call to haiku_sub_agent, if applicable
            if file_content_for_haiku and not haiku_tasks:
                sub_task_prompt = f"{sub_task_prompt}\n\nFile content:\n{file_content_for_haiku}"
            # Call haiku_sub_agent with the prepared prompt and record the result
            sub_task_result = haiku_sub_agent(sub_task_prompt, haiku_tasks)
            # Log the task and its result for future reference
            haiku_tasks.append({"task": sub_task_prompt, "result": sub_task_result})
            # Record the exchange for processing and output generation
            task_exchanges.append((sub_task_prompt, sub_task_result))
            # Prevent file content from being included in future haiku_sub_agent calls
            file_content_for_haiku = None

    # Create the .md filename
    sanitized_objective = re.sub(r'\W+', '_', objective)
    timestamp = datetime.now().strftime("%H-%M-%S")

    # Call Opus to review and refine the sub-task results
    refined_output = opus_refine(objective, [result for _, result in task_exchanges], timestamp, sanitized_objective)

    # Extract the project name from the refined output
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
    
    # Truncate the sanitized_objective to a maximum of 50 characters
    max_length = 25
    truncated_objective = sanitized_objective[:max_length] if len(sanitized_objective) > max_length else sanitized_objective

    # Update the filename to include the project name
    filename = f"../results/{timestamp}_{truncated_objective}.md"

    # Prepare the full exchange log
    exchange_log = f"Objective: {objective}\n\n"
    exchange_log += "=" * 40 + " Task Breakdown " + "=" * 40 + "\n\n"
    for i, (prompt, result) in enumerate(task_exchanges, start=1):
        exchange_log += f"Task {i}:\n"
        exchange_log += f"Prompt: {prompt}\n"
        exchange_log += f"Result: {result}\n\n"

    exchange_log += "=" * 40 + " Refined Final Output " + "=" * 40 + "\n\n"
    exchange_log += refined_output

    console.print(f"\n[bold]Refined Final output:[/bold]\n{refined_output}")

    with open(filename, 'w') as file:
        file.write(exchange_log)
    print(f"\nFull exchange log saved to {filename}")

    return files

