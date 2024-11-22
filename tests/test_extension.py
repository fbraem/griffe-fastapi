"""Test the griffe-fastapi extension."""

from griffe import Extensions, temporary_visited_package
from griffe_fastapi import FastAPIExtension


def test_extension() -> None:
    code = """
        from fastapi import ApiRouter

        router = APIRouter()

        @router.get("/teams", responses={200:{"description": "Ok"}}) 
        def get_teams() -> list[str]:
            '''Get the teams.
            '''
            return []
    """

    with temporary_visited_package(
        "package",
        modules={"__init__.py": code},
        extensions=Extensions(FastAPIExtension(generate_table=False)),
    ) as package:
        assert package
        assert package.functions["get_teams"]
        assert package.functions["get_teams"].extra is not None
        assert "griffe_fastapi" in package.functions["get_teams"].extra
        extra = package.functions["get_teams"].extra["griffe_fastapi"]
        assert extra["method"] == "get"
        assert extra["api"] == "/teams"
        assert extra["responses"]["200"]["description"] == "Ok"


def test_extension_with_constant() -> None:
    code = """
        from fastapi import ApiRouter, status

        router = APIRouter()

        @router.get("/teams", responses={status.HTTP_200_OK:{"description": "Ok"}}) 
        def get_teams() -> list[str]:
            '''Get the teams.'''
            return []
    """

    with temporary_visited_package(
        "package",
        modules={"__init__.py": code},
        extensions=Extensions(FastAPIExtension(generate_table=False)),
    ) as package:
        assert package
        assert package.functions["get_teams"]
        assert package.functions["get_teams"].extra is not None
        assert "griffe_fastapi" in package.functions["get_teams"].extra
        extra = package.functions["get_teams"].extra["griffe_fastapi"]
        assert extra["method"] == "get"
        assert extra["responses"]["200"]["description"] == "Ok"


def test_extension_with_multiple_responses() -> None:
    code = """
        from fastapi import ApiRouter

        router = APIRouter()

        @router.get("/teams", responses={
            200:{"description": "Ok"},
            404:{"description": "Not found"}
        }) 
        def get_teams() -> list[str]:
            '''Get the teams.'''
            return []
    """

    with temporary_visited_package(
        "package",
        modules={"__init__.py": code},
        extensions=Extensions(FastAPIExtension(generate_table=False)),
    ) as package:
        assert package
        assert package.functions["get_teams"]
        assert package.functions["get_teams"].extra is not None
        assert "griffe_fastapi" in package.functions["get_teams"].extra
        extra = package.functions["get_teams"].extra["griffe_fastapi"]
        assert extra["method"] == "get"
        assert extra["responses"]["200"]["description"] == "Ok"
        assert extra["responses"]["404"]["description"] == "Not found"


def test_extension_with_a_response_with_headers() -> None:
    code = """
        from fastapi import ApiRouter

        router = APIRouter()

        @router.get("/teams", responses={
            200:{"description": "Ok", "content": {"image/png": {}}},
            404:{"description": "Not found"}
        }) 
        def get_image() -> list[str]:
            '''Get the image.'''
            return []
    """

    with temporary_visited_package(
        "package",
        modules={"__init__.py": code},
        extensions=Extensions(FastAPIExtension(generate_table=False)),
    ) as package:
        assert package
        assert package.functions["get_image"]
        assert package.functions["get_image"].extra is not None
        assert "griffe_fastapi" in package.functions["get_image"].extra
        extra = package.functions["get_image"].extra["griffe_fastapi"]
        assert extra["method"] == "get"
        assert extra["responses"]["200"]["description"] == "Ok"
        assert extra["responses"]["200"]["content"] == {"image/png": {}}
        assert extra["responses"]["404"]["description"] == "Not found"


def test_extension_with_a_dict() -> None:
    code = """
        from fastapi import ApiRouter

        router = APIRouter()

        responses = {
            200: {"description": "Ok"},
            404: {"description": "Not Found"},
        }

        @router.get("/teams", responses={**responses}) 
        def get_teams() -> list[str]:
            '''Get the teams.'''
            return []
    """

    with temporary_visited_package(
        "package",
        modules={"__init__.py": code},
        extensions=Extensions(FastAPIExtension(generate_table=False)),
    ) as package:
        assert package
        assert package.functions["get_teams"]
        assert package.functions["get_teams"].extra is not None
        assert "griffe_fastapi" in package.functions["get_teams"].extra
        extra = package.functions["get_teams"].extra["griffe_fastapi"]
        assert extra["method"] == "get"
        assert extra["responses"]["200"]["description"] == "Ok"
        assert extra["responses"]["404"]["description"] == "Not Found"


def test_extension_mixed() -> None:
    code = """
        from fastapi import ApiRouter

        router = APIRouter()

        responses = {
            200: {"description": "Ok"}
        }

        @router.get("/teams", responses={404: {"description": "Not Found"}, **responses}) 
        def get_teams() -> list[str]:
            '''Get the teams.'''
            return []
    """

    with temporary_visited_package(
        "package",
        modules={"__init__.py": code},
        extensions=Extensions(FastAPIExtension(generate_table=False)),
    ) as package:
        assert package
        assert package.functions["get_teams"]
        assert package.functions["get_teams"].extra is not None
        assert "griffe_fastapi" in package.functions["get_teams"].extra
        extra = package.functions["get_teams"].extra["griffe_fastapi"]
        assert extra["method"] == "get"
        assert extra["responses"]["200"]["description"] == "Ok"
        assert extra["responses"]["404"]["description"] == "Not Found"


def test_with_paths() -> None:
    code = """
        from fastapi import ApiRouter

        router = APIRouter()

        @router.get("/teams", responses={200:{"description": "Ok"}}) 
        def get_teams() -> list[str]:
            '''Get the teams.'''
            return []
    """

    with temporary_visited_package(
        "package",
        modules={"__init__.py": code},
        extensions=Extensions(
            FastAPIExtension(paths=["package"], generate_table=False)
        ),
    ) as package:
        assert package
        assert package.functions["get_teams"]
        assert package.functions["get_teams"].extra["griffe_fastapi"] is not None


def test_extension_with_table() -> None:
    code = """
        from fastapi import ApiRouter

        router = APIRouter()

        @router.get("/teams", responses={200:{"description": "Ok"}}) 
        def get_teams() -> list[str]:
            '''Get the teams.
            '''
            return []
    """

    with temporary_visited_package(
        "package",
        modules={"__init__.py": code},
        extensions=Extensions(FastAPIExtension()),
    ) as package:
        assert package
        assert package.functions["get_teams"]
        assert package.functions["get_teams"].extra is not None
        assert "griffe_fastapi" in package.functions["get_teams"].extra
        extra = package.functions["get_teams"].extra["griffe_fastapi"]
        assert extra["method"] == "get"
        assert extra["responses"]["200"]["description"] == "Ok"
        assert (
            package.functions["get_teams"].docstring.parsed[1].value
            == "This api can return the following HTTP codes:\n\n| Status | Description |\n|--------|-------------|\n| 200 | Ok |"
        )
