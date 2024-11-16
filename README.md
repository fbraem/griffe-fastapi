Griffe FastAPI Extension
========================

This extension will search for functions that are decorated with an APIRouter and adds the following extra
fields to a function:

+ method: the HTTP method
+ responses: A dictionary with the responses

These fields are stored in the extra property of the function. The extra property is a dictionary and `griffe_fastapi`
is the key for the fields of this extension.

Create a custom function template to handle these extra fields in your documentation.

Installation
------------

````
pip install griffe-fastapi
````

or with poetry:

````
poetry add griffe-fastapi -G docs
````

When you use a group, like above, you also need to install it:

````
poetry install -G docs
````

MkDocs
------

````
plugins:
- mkdocstrings:
    handlers:
      python:
        options:
          extensions:
          - griffe_fastapi
````
