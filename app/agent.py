import os
from rich.console import Console
from rich.panel import Panel
from openai import OpenAI

MODEL = "gpt-4o"

chain = OpenAI(
    api_key=os.environ['OPENAI_API_KEY']
)

console = Console()

# it orchestrates the prompts by generating the first sub-tasks and reviewing the code generated. It also understands if all sub-tasks were applied, if so it terminates the looping
def gpt_orchestrator(objective, previous_results=None):
    console.print(f"\n[bold]Calling Orchestrator for your objective[/bold]")
    previous_results_text = "\n".join(previous_results) if previous_results else "None"
    
    messages = [
        {
            "role": "system",
            "content": "You are an AI orchestrator that breaks down frontend objectives into minimal, executable sub-tasks."
        },
        {
            "role": "user",
            "content": f""""
                Based on the following objective and the previous sub-task results (if any), please break down the objective for the next sub-task, and create a concise and detailed prompt for a 
                subagent so it can execute that task.
                IMPORTANT!!!
                    - When dealing with code tasks make sure only HTML and Javascript are generated and style with bootstrap css adding its CDN;
                        - Use only this bootstrap link tag for styling: <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@3.3.7/dist/css/bootstrap.min.css" crossorigin="anonymous">
                    - Never write backend code, focus only on frontend, even if you need to save anything, do it on frontend in memory;
                    - Check the code generated for errors and provide fixes and support as part of the next sub-task;
                    - If any bugs are found or have you suggestions for better code, please include them in the next sub-task prompt;
                    - Make sure all objectives were fully achieved;
                    - If the previous sub-task results comprehensively address all aspects of the objective and code is fully working with no bugs, 
                    include the phrase 'The task is complete:' at the beginning of your response;
                    - If the objective is not yet fully achieved, break it down into the next sub-task and create a concise and detailed prompt for a subagent to execute that task.
                
                Objective: {objective}
                Previous sub-task results: {previous_results_text}
            """
        }
    ]
    
    gpt_response = chain.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.7,
    )

    response_text = gpt_response.choices[0].message.content
    console.print(Panel(response_text, title=f"[bold green]Open AI Orchestrator[/bold green]", title_align="left", border_style="green", subtitle="Sending task to Subagent 👇"))
    
    return response_text

# agent to generate the code itself
def gpt_sub_agent(prompt, previous_gpt_tasks=None):
    if previous_gpt_tasks is None:
        previous_gpt_tasks = []

    system_message = "Previous Gpt tasks:\n" + "\n".join(f"Task: {task['task']}\nResult: {task['result']}" for task in previous_gpt_tasks)
    messages = [
        {
            "role": "system",
            "content": system_message
            },
        {
            "role": "user",
            "content": prompt
        }
    ]

    gpt_response = chain.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.7,
    )

    response_text = gpt_response.choices[0].message.content
    console.print(Panel(response_text, title="[bold blue]Open AI Sub-agent Result[/bold blue]", title_align="left", border_style="blue", subtitle="Task completed, sending result to Orchestrator 👇"))
    return response_text

# agent to refine/review the tasks and the code, generate all file names and prepare the code to be copied and pasted into the correct files
def gpt_refine(objective, sub_task_results):
    print('REFINE', sub_task_results)

    console.print("\nCalling gpt to provide the refined final output for your objective:")
    messages = [
        {
            "role": "system",
            "content": "You are an AI assistant that refines frontend related sub-task results into a cohesive final output."
        },
        {
            "role": "user",
            "content": f"""
                Objective: {objective}
                Sub-task results: {sub_task_results}
                
                Please review and refine the sub-task results into a cohesive final output. Add any missing information or details as needed. 
                Make sure the code files are completed. When working on code projects, ONLY AND ONLY IF THE PROJECT IS CLEARLY A CODING ONE please provide the following:
                
                1. Project Name: Create a concise and appropriate project name that fits the project based on what it's creating. The project name should be no more than 
                20 characters long.
                
                2. Folder Structure: Provide the folder structure as a valid JSON object, where each key represents a file (all files should have no folder). 
                Use null values for files. Ensure the JSON is properly formatted without any syntax errors. Please make sure all keys are enclosed in double quotes, 
                and ensure objects are correctly encapsulated with braces, separating items with commas as necessary.
                Wrap the JSON object in <folder_structure> tags.
                
                3. Code Files: For each code file, include ONLY the file name in this format 'Filename: <filename>' NEVER EVER USE THE FILE PATH OR ANY OTHER FORMATTING 
                YOU ONLY USE THE FOLLOWING format 'Filename: <filename>' followed by the code block enclosed in triple backticks, with the language identifier after the 
                opening backticks, like this:\n\njavascript\n<code>\n​
            """
        }
    ]

    # gpt_response = chain.invoke(messages)
    gpt_response = chain.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.7,
    )
    
    response_text = gpt_response.choices[0].message.content
    console.print(Panel(response_text, title="[bold green]Final Output[/bold green]", title_align="left", border_style="green"))
    return response_text