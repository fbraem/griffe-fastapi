"""griffe_fastapi extension."""

import ast
from typing import Any
from griffe import (
    Decorator,
    Docstring,
    DocstringSectionText,
    ExprAttribute,
    ExprCall,
    ExprDict,
    ExprKeyword,
    ExprName,
    Extension,
    Function,
    Inspector,
    ObjectNode,
    Visitor,
    get_logger,
)

self_namespace = "griffe_fastapi"

logger = get_logger(__name__)


def _search_decorator(func: Function) -> Decorator | None:
    """Search for a APIRouter decorator."""
    decorators = list(
        filter(
            lambda d: d.value.canonical_name in ("get", "post", "patch", "delete"),
            func.decorators,
        )
    )
    if len(decorators) == 0:
        return None

    for decorator in decorators:
        if not isinstance(decorator.value, ExprCall):
            continue

        if not isinstance(decorator.value.function, ExprAttribute):
            continue

        if not isinstance(decorator.value.function.first, ExprName):
            continue

        module = decorator.value.function.first.parent
        if decorator.value.function.first.name not in module.members:
            continue

        type_ = module.members[decorator.value.function.first.name].value.canonical_name
        if type_ == "APIRouter":
            return decorator

    return None


def _resolve_http_code(func, http_code: str | ExprAttribute):
    """When http code is an attribute, try to get the value."""
    if isinstance(http_code, ExprAttribute):
        if http_code.canonical_path.startswith("fastapi.status."):
            return http_code.last.name.split("_")[1]
        logger.warning(
            f"Could not resolve http code {http_code.canonical_path} "
            f"for function {func.canonical_path}"
        )
        return
    return http_code


def _process_responses(
    func: Function,
    http_code: str,
    open_api_response: ExprName | ExprDict,
):
    """Process the response code and the response object."""
    func.extra[self_namespace]["responses"][http_code] = {
        ast.literal_eval(str(key)): ast.literal_eval(str(value))
        for key, value in zip(
            open_api_response.keys,
            open_api_response.values,
            strict=True,
        )
    }


class FastAPIExtension(Extension):
    def __init__(self, *, paths: list[str] | None = None, generate_table: bool = True):
        """Initialize the extension.

        Args:
            paths: A list of paths to select api functions
            generate_table: Generate the table at the end of the function docstring?
        """
        super().__init__()
        self._paths = paths or []
        self._generate_table = generate_table

    def on_function_instance(
        self,
        *,
        node: ast.AST | ObjectNode,
        func: Function,
        agent: Visitor | Inspector,
        **kwargs: Any,
    ) -> None:
        """Implement the function instance handler."""

        # When paths is set, skip functions that are not part of the path.
        if self._paths:
            if not any(func.path.startswith(path) for path in self._paths):
                return

        decorator = _search_decorator(func)
        if decorator is None:
            return

        func.extra[self_namespace] = {"method": decorator.value.canonical_name}

        # Search the "responses" keyword in the arguments of the function.
        responses = next(
            (
                x
                for x in decorator.value.arguments
                if isinstance(x, ExprKeyword) and x.name == "responses"
            ),
            None,
        )
        if responses is None:
            logger.warning(
                f"No responses argument found for function {func.canonical_path}"
            )
            return
        if not isinstance(responses.value, ExprDict):
            logger.warning(
                f"responses argument is not a dict for function {func.canonical_path}"
            )
            return

        resolved_responses = {}

        for http_code_variable, open_api_response_obj in zip(
            responses.value.keys, responses.value.values, strict=True
        ):
            # When the response contains a variable, try to resolve it.
            if isinstance(open_api_response_obj, ExprName):
                module_attribute = func.module.members[open_api_response_obj.name]
                if isinstance(module_attribute.value, ExprDict):
                    resolved_responses = {
                        **resolved_responses,
                        **{
                            k: _resolve_http_code(func, v)
                            for k, v in zip(
                                module_attribute.value.keys,
                                module_attribute.value.values,
                            )
                        },
                    }
            else:
                http_code = _resolve_http_code(func, http_code_variable)
                resolved_responses[http_code] = open_api_response_obj

        func.extra[self_namespace]["responses"] = {}
        for key, value in resolved_responses.items():
            _process_responses(func, key, value)

        if self._generate_table:
            table = [
                "| Status | Description |",
                "|--------|-------------|",
            ]
            for http_code, response in func.extra[self_namespace]["responses"].items():
                table.append(f"| {http_code} | {response['description']} |")
            if not func.docstring:
                func.docstring = Docstring("", parent=func)
            sections = func.docstring.parsed
            sections.append(
                DocstringSectionText(
                    f"This api can return the following HTTP codes:\n\n{table}",
                    title="HTTP Responses",
                )
            )
