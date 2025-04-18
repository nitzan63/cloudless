import textwrap
import ast
import logging
import ray

logger = logging.getLogger(__name__)


class ScriptProcessor:
    def __init__(self):
        """Initialize the script processor service"""
        pass

    def wrap_script(self, script_content: str):
        """
        Wrap the script content with Ray remote decorator and proper function structure.
        The script should contain a main(file_path, **kwargs) function.
        
        Args:
            script_content: String containing the Python script
            
        Returns:
            A Ray remote function ready to be executed
        """
        # Validate the script first
        if not self.validate_script(script_content):
            raise ValueError("Invalid script: Must contain a main(file_path, **kwargs) function")

        # Create a namespace for the script
        script_namespace = {}
        
        # Execute the original script to define the main function
        exec(script_content, script_namespace)
        
        # Get the main function
        main_func = script_namespace['main']
        
        # Create the wrapped function
        @ray.remote
        def execute_user_script(file_path: str, **kwargs):
            try:
                result = main_func(file_path, **kwargs)
                return {"status": "success", "result": result}
            except Exception as e:
                return {"status": "error", "error": str(e)}
        
        return execute_user_script

    def validate_script(self, script_content: str) -> bool:
        """
        Validate the script content:
        - Check if it's valid Python syntax
        - Verify it has a main function
        - Verify main function accepts required arguments
        
        Args:
            script_content: String containing the Python script
            
        Returns:
            bool: True if script is valid, False otherwise
        """
        try:
            logger.info(f"Validating script: \n{script_content}")
            # Parse the script into an AST
            tree = ast.parse(script_content)
            
            # Look for main function definition
            main_func = None
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == 'main':
                    main_func = node
                    break
            
            if main_func is None:
                logger.error("No main function found in script")
                return False
                
            # Check main function arguments
            args = main_func.args
            if not args.args or args.args[0].arg != 'file_path':
                logger.error("Main function does not accept file_path argument")
                return False
                
            return True
            
        except SyntaxError as e:
            logger.error(f"SyntaxError: {e}")
            return False
        except Exception as e:
            logger.error(f"Exception: {e}")
            return False

    def validate_wrapped_script(self, wrapped_script: str) -> bool:
        """
        Validate the wrapped script structure:
        - Check if it's valid Python syntax
        - Verify it has the execute_user_script function
        - Verify execute_user_script has correct arguments
        - Verify it contains the main function call
        - Verify it has proper error handling
        
        Args:
            wrapped_script: String containing the wrapped script
            
        Returns:
            bool: True if wrapped script is valid, False otherwise
        """
        try:
            logger.info(f"Validating wrapped script: \n{wrapped_script}")
            # Parse the wrapped script into an AST
            tree = ast.parse(wrapped_script)
            
            # Look for execute_user_script function
            execute_func = None
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == 'execute_user_script':
                    execute_func = node
                    break
            
            if execute_func is None:
                logger.error("No execute_user_script function found in wrapped script")
                return False
                
            # Check execute_user_script arguments
            args = execute_func.args
            if not args.args or args.args[0].arg != 'file_path':
                logger.error("execute_user_script function does not accept file_path argument")
                return False
                
            # Check for main function call
            has_main_call = False
            has_error_handling = False
            for node in ast.walk(execute_func):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'main':
                    has_main_call = True
                if isinstance(node, ast.Try):
                    has_error_handling = True
                    
            if not (has_main_call and has_error_handling):
                logger.error("execute_user_script function does not have main call or error handling")
                return False
                
            return True
            
        except SyntaxError as e:
            logger.error(f"SyntaxError in wrapped script: {e}")
            return False
        except Exception as e:
            logger.error(f"Exception in wrapped script validation: {e}")
            return False