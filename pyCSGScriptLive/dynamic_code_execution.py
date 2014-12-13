import sys
import ast
import string
import re
import traceback
import itertools
from Queue import Queue
from StringIO import StringIO
from threading import Thread

class BaseCodeChecker(object):
    """This class parses the code for syntax errors, and if no error \
    was detected calls the runs the code executor.
    """
    
    _statement_fix_table = [("class", "class C():"),
                            ("def", "def f(self):"),
                            ("if", "if True:"),
                            ("else", "else:"),
                            ("elif", "elif True:"),
                            ("try", "try:"),
                            ("except", "except:"),
                            ("for", "for i in range(0, 0)"),
                            ("while", "while True:")]
    
    # Request types
    class CheckRequest():
        def __init__(self, code, filename = "<unknown>", execute = False):
            self.code = code
            self.filename = filename
            self.execute = execute
        pass
    
    class TermRequest():
        pass
    
    def __init__(self, code_executor):
        
        # The code executor to run the code
        self._code_executor = code_executor
        
        # Thread for code checking
        self._check_thread = None
        
        # The queue of the requests
        self._requests_queue = Queue()
        
        # Store a list of syntax_errors detected during the last parse
        self._syntax_errors = []
        
    @property
    def syntax_errors(self):
        """A list of syntax_errors detected during the last parse of the \
        code."""
        return self._syntax_errors
    
    def on_parse_start(self):
        """This method is called just before the parsing has started.
        
        You can override it to implement your functionalities, such as
        signaling this event with your event or signal system to 
        other objects.
        IMPORTANT: This method is calls by an internal Thread.
        
        """
        pass
    
    def on_parse_end(self):
        """This method is called just after the parsing is terminated.
        
        You can override it to implement your functionalities, such as
        signaling this event with your event or signal system to 
        other objects.
        IMPORTANT: This method is calls by an internal Thread.
        
        """
        pass
    
    def send_request(self, request):
        """Send a request to the checking thread.
        
        request must be a supported request object.
        If the thread is not running this method runs it.
        
        """
        self._requests_queue.put(request)
        
        if not self._check_thread or not self._check_thread.is_alive():
            self._check_thread = Thread(target=self._thread_loop)
            self._check_thread.start()
        
    def _thread_loop(self):
        # The main thread loop, wait for a request and process it
        
        while True:
            request = self._requests_queue.get()
            if isinstance(request, BaseCodeChecker.TermRequest):
                return
            elif isinstance(request, BaseCodeChecker.CheckRequest):
                self.on_parse_start()
                self._check_code(request.code, request.filename,
                                 request.execute)
                self.on_parse_end()
        
    def _check_code(self, code, filename, execute):
        # Parse the code for syntax errors, if no error has been
        # detected then make a request to the code executor.
        
        code_ast = None
        error = None
        syntax_errors = []
        code_lines = None

        # If the first parse fail keep looping to detect multiple errors
        while not code_ast:
            try:
                # Generate an AST object from code
                code_ast = ast.parse(code, filename)
            except SyntaxError as e:
                # Prevent and infinite loop if fixing failed
                if error and e.lineno == error.lineno:
                    break
                # A request has arrived, so process it
                if not self._requests_queue.empty():
                    break
                error = e
                syntax_errors.append(error)
                if not code_lines:
                    code_lines = code.split("\n")
                BaseCodeChecker._fix_error(error, code_lines)
                code = "\n".join(code_lines)
    
        if not error and execute:
            exec_request = BaseCodeExecutor.ExecRequest(code_ast, filename)
            self._code_executor.send_request(exec_request)
            
        self._syntax_errors = syntax_errors
    
    @classmethod
    def _fix_error(cls, error, lines):
        # Try to fix the syntactical error with a dummy but
        # syntactical correct statement
        
        error_lineno = error.lineno - 1
        line_text = lines[error_lineno]
        for statement_fix in BaseCodeChecker._statement_fix_table:
            pos = string.find(line_text, statement_fix[0])
            if pos >= 0:
                line_text = line_text[:pos] + statement_fix[1]
                break
        else:
            match = re.search("\S", line_text)
            if match:
                pos = match.start(0)
            else:
                return
            line_text = line_text[:pos] + "pass"
        lines[error_lineno] = line_text
    
    
class BaseCodeExecutor(object):
    """This class can execute arbitrary code provided as an AST.
    
    The class store the execution state and attempt to not execute
    the code if the provided AST has the same structure of the last
    executed AST or to only execute appended nodes if the provided AST
    has the same structure of the last AST executed AST,
    plus some nodes appended.
    If this is not possible the execution state is reset and the
    execution is performed form the very start of the code.
    
    """
    
    # Request types
    class ExecRequest():
        def __init__(self, code_ast, filename):
            self.code_ast = code_ast
            self.filename = filename
            
    class StopRequest():
        pass
    
    class TermRequest():
        pass
    
    def __init__(self, exec_stdout = None, exec_stderr = None):
        
        # Execution stderr and stdout
        default_output = StringIO()
        if not exec_stdout:
            exec_stdout = default_output
        if not exec_stderr:
            exec_stderr = default_output
        
        self.exec_stdout = exec_stdout
        self.exec_stderr = exec_stderr
        
        # Execution raised exception
        self.exec_exception = None
        
        # Execution dictionaries
        self.exec_globals = {}
        self.exec_locals = {}
        
        # The previous executed code AST
        self._code_ast = ast.AST()
        
        # The length of the code_ast body if present
        self._body_len = -1
        
        # The filename for the code to compile with
        self._filename = "<unknown>"
        
        # True if a stop request has been performed
        self._requests_queue = Queue()
        
        # The index of the next node to be executed
        self._next_node_index = 0
        
        # Cache for compiled AST nodes
        self._compiled_cache = []
        
        # Thread for code execution
        self._exec_thread = None
        
    def on_execution_reset(self):
        """This method is called after the execution has been reset.
        
        You can override it to implement your functionalities, such as
        signaling this event with your event or signal system to 
        other objects.
        IMPORTANT: This method is calls by an internal Thread.
        
        """
        pass
    
    def on_execution_end(self):
        """This method is called when the execution reaches the end \
        of the file and is waiting for code changes.
        
        You can override it to implement your functionalities, such as
        signaling this event with your event or signal system to 
        other objects.
        IMPORTANT: This method is calls by an internal Thread.
        
        """
        pass
    
    def on_statemet_executed(self):
        """This method is called after a statement has been executed.
        
        You can override it to implement your functionalities, such as
        signaling this event with your event or signal system to 
        other objects.
        IMPORTANT: This method is calls by an internal Thread.
        
        """
        pass
        
    def send_request(self, request):
        """Send a request to the code executor.
                
        request must be a supported request object.
        If the thread is not running this method runs it.
        
        """
        
        self._requests_queue.put(request)
        
        # Starts the thread if not already running
        if not self._exec_thread or not self._exec_thread.is_alive():
            self._exec_thread = Thread(target=self._thread_loop)
            self._exec_thread.start()
        
    def _thread_loop(self):
        while True:
            request = self._requests_queue.get()
            if isinstance(request, BaseCodeExecutor.StopRequest):
                self._reset_execution()
            elif isinstance(request, BaseCodeExecutor.TermRequest):
                return
            elif isinstance(request, BaseCodeExecutor.ExecRequest):
                if request.filename != self._filename:
                    self._reset_execution()
                    self._filename = request.filename
                self._diff_ast(request.code_ast)
                self._run_code()
                if self.exec_exception:
                    self._reset_execution()
                
    def _diff_ast(self, code_ast):
        # Check if the code structure has changed and update
        # the internal variables accordingly
        
        diff_node_index = None
        try:
            nodes = itertools.izip_longest(code_ast.body, self._code_ast.body)
        except AttributeError:
            diff_node_index = -1
        else:
            for i, node in enumerate(nodes):
                if (node[0] and not node[1] or
                    not node[0] and node[1] or
                    ast.dump(node[0]) != ast.dump(node[1])):
                    
                    diff_node_index = i
                    break
        
        if diff_node_index is not None:
            self._code_ast = code_ast
            try:
                self._body_len = len(code_ast.body)
            except AttributeError:
                self._body_len = -1
            if diff_node_index < len(self._compiled_cache):
                self._compiled_cache = self._compiled_cache[:diff_node_index]
            if diff_node_index < self._next_node_index:
                self._reset_execution()
        
    def _run_code(self):
        # Code is run AST-node by AST-node.
        # If a request has been received the execution is stopped and 
        # the methods returns as soon as it can
            
        while True:
            
            if not self._requests_queue.empty():
                return
            elif self._next_node_index >= self._body_len:
                break
            elif self.exec_exception:
                break
            
            self._exec_next_node()
            self.on_statemet_executed()
            self._next_node_index += 1
        
        self.on_execution_end()
        
    def _exec_next_node(self):
        # Execute a singe node. If this node in within the cache 
        # than retrieve if from there and execute it, else
        # compile the node and adds it to the cache before execution
        
        if len(self._compiled_cache) > self._next_node_index:
            compiled_node = self._compiled_cache[self._next_node_index]
            self._wrapped_exec(compiled_node)
        else:
            node = self._code_ast.body[self._next_node_index]
            wrapper = ast.Module(body=[node])
            compiled = compile(wrapper, self._filename, "exec")
            if self._next_node_index == len(self._compiled_cache):
                self._compiled_cache.append(compiled)
            self._wrapped_exec(compiled)
            
    def _wrapped_exec(self, obj):
        # Capture the stdout and stderr of the execution
        # and set the execution dicitionaries.
        # Exception raised in the execution of obj are not
        # propagated, but just print in the captured stderr.
        
        sys.stdout = self.exec_stdout
        sys.stderr = self.exec_stderr
        try:
            exec(obj, self.exec_globals, self.exec_locals)
        except:
            traceback.print_exc(None, self.exec_stderr)
            
            # FIXME for some reason works in debugging mode but not
            # in normal running...
            #self.exec_exception = sys.exc_info()[1]
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
            
    def _reset_execution(self):
        # Clear the dicionaries with the execution state and sets
        # the next_node_index to zero, for a new execution.
        # Also notify that the execution will restart from the
        # beginning of the code.
        
        self.exec_globals = {}
        self.exec_locals = {}
        self.exec_stdout.truncate(0)
        self.exec_stderr.truncate(0)
        self._next_node_index = 0
        self.exec_exception = None
        self.on_execution_reset()
            