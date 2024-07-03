import os
from rich.console import Console
from rich.panel import Panel

console = Console()

def create_folder_structure(project_name, folder_structure, code_blocks, files = []):
    # Create the project folder
    try:
        os.makedirs(project_name, exist_ok=True)
        console.print(Panel(f"Created project folder: [bold]{project_name}[/bold]", title="[bold green]Project Folder[/bold green]", title_align="left", border_style="green"))
    except OSError as e:
        console.print(Panel(f"Error creating project folder: [bold]{project_name}[/bold]\nError: {e}", title="[bold red]Project Folder Creation Error[/bold red]", title_align="left", border_style="red"))
        return

    # Recursively create the folder structure and files
    create_folders_and_files(project_name, folder_structure, code_blocks, files)
    return files

def create_folders_and_files(current_path, structure, code_blocks, files):
    for key, value in structure.items():
        path = os.path.join(current_path, key)
        if isinstance(value, dict):
            try:
                os.makedirs(path, exist_ok=True)
                console.print(Panel(f"Created folder: [bold]{path}[/bold]", title="[bold blue]Folder Creation[/bold blue]", title_align="left", border_style="blue"))
                create_folders_and_files(path, value, code_blocks, files)
            except OSError as e:
                console.print(Panel(f"Error creating folder: [bold]{path}[/bold]\nError: {e}", title="[bold red]Folder Creation Error[/bold red]", title_align="left", border_style="red"))
        else:
            code_content = next((code for file, code in code_blocks if file.replace('*', '') == key), None)
            if code_content:
                try:
                    files.append(path)
                    with open(path, 'w') as file:
                        file.write(code_content)
                    console.print(Panel(f"Created file: [bold]{path}[/bold]", title="[bold green]File Creation[/bold green]", title_align="left", border_style="green"))
                except IOError as e:
                    console.print(Panel(f"Error creating file: [bold]{path}[/bold]\nError: {e}", title="[bold red]File Creation Error[/bold red]", title_align="left", border_style="red"))
            else:
                console.print(Panel(f"Code content not found for file: [bold]{key}[/bold]", title="[bold yellow]Missing Code Content[/bold yellow]", title_align="left", border_style="yellow"))
    return files

def read_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    return content