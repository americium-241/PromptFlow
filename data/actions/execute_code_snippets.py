from plugin_base import PluginBase
import io
from contextlib import redirect_stdout, redirect_stderr

class ExecuteCodeSnippetsPlugin(PluginBase):
    def __init__(self, di_container, debug=False):
        super().__init__(di_container, debug)
        self.register_action('execute_code_snippets', self.execute_code_snippets)

    def execute_code_snippets(self, *args, **kwargs):
        if self.debug:
            print("ExecuteCodeSnippetsPlugin: Executing execute_code_snippets")

        snippets = self.execute('container_get', 'snippets')
        
        if self.debug:
            print(f"ExecuteCodeSnippetsPlugin: Retrieved {len(snippets)} snippets")

        results = []
        for i, snippet in enumerate(snippets):
            if self.debug:
                print(f"ExecuteCodeSnippetsPlugin: Executing snippet {i+1}")

            local_env = {}
            global_env = {}
            try:
                output_capture = io.StringIO()
                error_capture = io.StringIO()
                with redirect_stdout(output_capture), redirect_stderr(error_capture):
                    exec(str(snippet[0]), global_env, local_env)
                output = output_capture.getvalue()
                error = error_capture.getvalue()
                result = {"output": output, "error": error, "env": local_env}
            except Exception as e:
                result = {"error": str(e), "env": local_env}
            
            results.append(result)
            print(results)

            if self.debug:
                print(f"ExecuteCodeSnippetsPlugin: Snippet {i+1} execution result: {result}")

        return results