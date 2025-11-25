# tools/calculator.py
import ast
import operator as op

# safe eval for basic arithmetic
# supported operators
operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.Mod: op.mod,
}

def safe_eval(expr: str):
    """
    Safely evaluate arithmetic expressions using ast parsing (no names, no calls).
    """
    def _eval(node):
        if isinstance(node, ast.Num):  # <number>
            return node.n
        if isinstance(node, ast.BinOp):
            return operators[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp):
            return operators[type(node.op)](_eval(node.operand))
        raise ValueError(f"Unsupported expression: {node!r}")

    node = ast.parse(expr, mode='eval').body
    return _eval(node)

def run(input_text: str) -> str:
    # try to extract expression heuristically
    expr = input_text.strip()
    # remove leading 'calculate' or 'what is'
    prefixes = ["calculate", "what is", "eval", "solve"]
    for p in prefixes:
        if expr.lower().startswith(p):
            expr = expr[len(p):].strip()
    try:
        val = safe_eval(expr)
        return str(val)
    except Exception as e:
        return f"Error evaluating expression: {e}"
