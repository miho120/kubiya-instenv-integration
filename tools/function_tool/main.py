import typer
from typing_extensions import Annotated

from kubiya_sdk.tools import function_tool


@function_tool(
    description="Prints pandas {name}!",
    requirements=["pandas==2.2.3"],
    secrets=["TEST_SECRET"],
)
def test_123(
    name: str,
    boolean_val: bool,  # This will validate that the input is a boolean
    optional_str: Annotated[str, typer.Argument()] = "sheeesh",  # This is how to add a default value
):
    import pandas as pd
    import os
    import base64

    print(f"Hello {name}! Request user: {os.environ.get('KUBIYA_USER_EMAIL', 'no user')}. Secret: {base64.b64encode(os.environ.get('TEST_SECRET', 'no secret').encode('ascii'))}. {boolean_val} {optional_str}")
    df = pd.DataFrame({"name": [name], "boolean_val": [boolean_val], "test": [optional_str]})

    print(df)
