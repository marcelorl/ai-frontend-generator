import os
from rich.console import Console
from rich.panel import Panel
from langchain_groq import ChatGroq

# Define the models to use for each agent
ORCHESTRATOR_MODEL = "mixtral-8x7b-32768"
SUB_AGENT_MODEL = "mixtral-8x7b-32768"
REFINER_MODEL = "llama3-70b-8192"

console = Console()

def opus_orchestrator(objective, file_content=None, previous_results=None):
    chain = ChatGroq(
        temperature=0.7,
        model_name=ORCHESTRATOR_MODEL,
        api_key=os.environ['GROQ_API_KEY']
    )

    console.print(f"\n[bold]Calling Orchestrator for your objective[/bold]")
    previous_results_text = "\n".join(previous_results) if previous_results else "None"
    if file_content:
        console.print(Panel(f"File content:\n{file_content}", title="[bold blue]File Content[/bold blue]", title_align="left", border_style="blue"))
    messages = [
        ("system",
            "You are an AI orchestrator that breaks down frontend objectives into minimal, executable sub-tasks."),
        ("user",
            f"Based on the following objective{' and file content' if file_content else ''}, and the previous sub-task results (if any), please break down the objective into the next sub-task, and create a concise and detailed prompt for a subagent so it can execute that task. IMPORTANT!!! when dealing with code tasks make sure you check the code for errors and provide fixes and support as part of the next sub-task and you only use HTML, Javascript always style using bootstrap CDN the following <link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css' crossorigin='anonymous'>. Never write backend code, focus only on frontend, even if you need to save anything, do it on frontend in memory. If you find any bugs or have suggestions for better code, please include them in the next sub-task prompt. Please assess if the objective has been fully achieved. If the previous sub-task results comprehensively address all aspects of the objective, include the phrase 'The task is complete:' at the beginning of your response. If the objective is not yet fully achieved, break it down into the next sub-task and create a concise and detailed prompt for a subagent to execute that task.:\n\nObjective: {objective}" + ('\\nFile content:\\n' + file_content if file_content else '') + f"\n\nPrevious sub-task results:\n{previous_results_text}")
    ]

    opus_response = chain.invoke(messages)

    response_text = opus_response.content
    console.print(Panel(response_text, title=f"[bold green]Groq Orchestrator[/bold green]", title_align="left", border_style="green", subtitle="Sending task to Subagent 👇"))
    return response_text, file_content

def haiku_sub_agent(prompt, previous_haiku_tasks=None):
    chain = ChatGroq(
        temperature=0.7,
        model_name=SUB_AGENT_MODEL,
        api_key=os.environ['GROQ_API_KEY']
    )

    if previous_haiku_tasks is None:
        previous_haiku_tasks = []

    system_message = "Previous Haiku tasks:\n" + "\n".join(f"Task: {task['task']}\nResult: {task['result']}" for task in previous_haiku_tasks)
    
    messages = [
        ("system",
            system_message),
        ("user",
            prompt)
    ]

    haiku_response = chain.invoke(messages)

    response_text = haiku_response.content
    console.print(Panel(response_text, title="[bold blue]Groq Sub-agent Result[/bold blue]", title_align="left", border_style="blue", subtitle="Task completed, sending result to Orchestrator 👇"))
    return response_text

def opus_refine(objective, sub_task_results, filename, projectname, continuation=False):
    chain = ChatGroq(
        temperature=0.7,
        model_name=REFINER_MODEL,
        api_key=os.environ['GROQ_API_KEY']
    )
    
    console.print("\nCalling Opus to provide the refined final output for your objective:")
    messages = [
        ("system",
            "You are an AI assistant that refines frontend related sub-task results into a cohesive final output."),
        ("user",
            "Objective: " + objective + "\n\nSub-task results:\n" + "\n".join(sub_task_results) + "\n\nPlease review and refine the sub-task results into a cohesive final output. Add any missing information or details as needed. Make sure the code files are completed. When working on code projects, ONLY AND ONLY IF THE PROJECT IS CLEARLY A CODING ONE please provide the following:\n1. Project Name: Create a concise and appropriate project name that fits the project based on what it's creating. The project name should be no more than 20 characters long.\n2. Folder Structure: Provide the folder structure as a valid JSON object, where each key represents a folder or file, and nested keys represent subfolders. Use null values for files. Ensure the JSON is properly formatted without any syntax errors. Please make sure all keys are enclosed in double quotes, and ensure objects are correctly encapsulated with braces, separating items with commas as necessary.\nWrap the JSON object in <folder_structure> tags.\n3. Code Files: For each code file, include ONLY the file name in this format 'Filename: <filename>' NEVER EVER USE THE FILE PATH OR ANY OTHER FORMATTING YOU ONLY USE THE FOLLOWING format 'Filename: <filename>' followed by the code block enclosed in triple backticks, with the language identifier after the opening backticks, like this:\n\n​python\n<code>\n​")
    ]

    opus_response = chain.invoke(messages)
    
    response_text = opus_response.content
    console.print(Panel(response_text, title="[bold green]Final Output[/bold green]", title_align="left", border_style="green"))
    return response_text