import ast
from dataclasses import dataclass
from typing import List, Set


@dataclass
class Issue:
    line: int
    rule_id: str
    message: str


class FlakyTestVisitor(ast.NodeVisitor):

    def __init__(self, raw_code: str):
        self.raw_code = raw_code
        self.lines = raw_code.splitlines()
        self.issues: List[Issue] = []

        # Track aliases for imports
        self.sleep_aliases: Set[str] = set()
        self.random_aliases: Set[str] = set()
        self.has_random_seed = False

    def _is_suppressed(self, lineno: int) -> bool:
        if 1 <= lineno <= len(self.lines):
            return "# flaky: ignore" in self.lines[lineno - 1]
        return False

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            name = alias.asname or alias.name
            if alias.name == "time":
                self.sleep_aliases.add(f"{name}.sleep")
            elif alias.name == "random":
                self.random_aliases.add(name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module == "time":
            for alias in node.names:
                if alias.name == "sleep":
                    self.sleep_aliases.add(alias.asname or "sleep")
        elif node.module == "random":
            for alias in node.names:
                if alias.name == "seed":
                    self.has_random_seed = True
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        if self._is_suppressed(node.lineno):
            self.generic_visit(node)
            return

        # 1. Detect time.sleep()
        func_name = ""
        if isinstance(node.func, ast.Attribute) and isinstance(
            node.func.value, ast.Name
        ):
            func_name = f"{node.func.value.id}.{node.func.attr}"
        elif isinstance(node.func, ast.Name):
            func_name = node.func.id

        if func_name in self.sleep_aliases:
            self.issues.append(
                Issue(
                    line=node.lineno,
                    rule_id="FLK001",
                    message="Hardcoded time.sleep() found. Race conditions occur if execution outpaces sleep. Use polling or explicit waits.",
                )
            )

        # 2. Detect unseeded random module usage
        if (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id in self.random_aliases
        ):
            if node.func.attr == "seed":
                self.has_random_seed = True
            elif not self.has_random_seed and node.func.attr != "seed":
                self.issues.append(
                    Issue(
                        line=node.lineno,
                        rule_id="FLK002",
                        message=f"Unseeded `random.{node.func.attr}()` call. Test outcomes will vary per execution. Set a static random.seed().",
                    )
                )

        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign):
        if self._is_suppressed(node.lineno):
            self.generic_visit(node)
            return

        # 3. Detect os.environ modifications (Shared State mutation)
        for target in node.targets:
            if isinstance(target, ast.Subscript) and isinstance(
                target.value, ast.Attribute
            ):
                if (
                    isinstance(target.value.value, ast.Name)
                    and target.value.value.id == "os"
                    and target.value.attr == "environ"
                ):
                    self.issues.append(
                        Issue(
                            line=node.lineno,
                            rule_id="FLK003",
                            message="Mutation of global state (`os.environ`). Parallel execution or test re-ordering can corrupt adjacent tests.",
                        )
                    )

        self.generic_visit(node)


def analyze_code(source: str) -> List[Issue]:
    tree = ast.parse(source)
    visitor = FlakyTestVisitor(source)
    visitor.visit(tree)
    return visitor.issues