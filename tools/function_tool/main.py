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


@function_tool(
    description="Get failed environment logs from InstEnv",
    requirements=["requests==2.26.0"],
    secrets=["INSTENV_API_TOKEN"],
)
def get_instenv_logs(
    environment_id: str,
    run_id: Annotated[str, typer.Argument()] = None,
):
    import requests
    import os

    env_url = f"https://prod.instenv-ui.internal.atlassian.com/api/v2/environments/{environment_id}"
    headers = {
        'Authorization': f"Bearer {os.environ.get('INSTENV_API_TOKEN')}"
    }

    configuration_response = requests.get(
        env_url,
        headers=headers
    )
    if configuration_response.status_code != 200:
        print(f"Failed to get configuration for environment {environment_id}")
        return

    configuration = configuration_response.json()

    # Get the latest failed run id
    failed_run_id = run_id
    if failed_run_id is None:
        for run in configuration["runs"]:
            if run.get("status") in ["failed", "running-failed"]:
                failed_run_id = run.get("id")
                break

    if failed_run_id is None:
        print(f"No failed runs found for environment {environment_id}")
        return

    # Get the logs for the failed run
    logs_url = (f"https://prod.instenv-ui.internal.atlassian.com/api"
                f"/v2/environments/{environment_id}/runs/{failed_run_id}/logs")
    logs_response = requests.get(
        logs_url,
        headers=headers
    )
    if logs_response.status_code != 200:
        print(f"Failed to get logs for run {failed_run_id}")
        return

    logs = logs_response.text.replace("\\n", "\n")
    # Get the last 100 lines of logs
    print("\n".join(logs.split("\n")[-100:]))

if __name__ == "__main__":
    typer.run(get_instenv_logs)