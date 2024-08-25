import asyncio
import argparse
import importlib

commands = {
    "populate_missing_urls": "scrapper.commands.update_request_tracker",
    "run_query": "scrapper.commands.update_request_tracker"
}

def to_pascal_case(snake_str):
    return ''.join(word.capitalize() for word in snake_str.split('_'))

def main():
    parser = argparse.ArgumentParser(description="Process some arguments.")
    parser.add_argument('--command_name', type=str, required=True, help='Name of the job')

    args = parser.parse_args()

    command_name = args.command_name
    cls = None
    try:
        module_name = ""
        if command_name in commands:
            module_name = f"{commands[command_name]}"
        else:
            raise ModuleNotFoundError

        module = importlib.import_module(module_name)
        
        class_name = to_pascal_case(snake_str=command_name)
        cls = getattr(module, class_name)
    except ImportError:
        print(f"Module '{module_name}' not found.")
    except AttributeError:
        print(f"Class '{class_name}' not found in module '{module_name}'.")

    try:
        obj = cls()
        if hasattr(obj, "init") and callable(getattr(obj, "init")):
            asyncio.run(obj.init())
    except AttributeError as err:
        print(f"Class {obj.__class__.__name__} has no attribute init")
    except TypeError as err:
        print(f"{err}")
    
if __name__ == '__main__':
    main()