import typer
from kubiya_sdk.tools import function_tool
from typing_extensions import Annotated


@function_tool(
    description="Get failed environment logs from InstEnv",
    requirements=["requests==2.26.0"],
    secrets=["INSTENV_API_TOKEN"],
)
def get_instenv_logs(
    environment_id: str,
):
    import requests
    import os

    class InstEnvHelper:
        __API_URL = "https://prod.instenv-ui.internal.atlassian.com/api/v2"
        __env_configurations = None

        def __init__(self, env_id: str, env_run_id:str=None):
            self.environment_id = env_id
            self.run_id = env_run_id
            self.headers = {
                'Authorization': f"Bearer {os.environ.get('INSTENV_API_TOKEN')}"
            }

        def __make_request(self, endpoint: str, method: str = "GET"):
            url = f"{self.__API_URL}/{endpoint}"
            response = requests.request(
                method,
                url,
                headers=self.headers
            )
            return response

        def get_environment_configuration(self):
            response = self.__make_request(f"/environments/{self.environment_id}")
            self.__env_configurations = response.json()
            return self.__env_configurations

        def get_last_failed_run_id(self):
            if self.run_id:
                return self.run_id

            if not self.__env_configurations:
                self.get_environment_configuration()

            for run in self.__env_configurations.get("runs", []):
                if run.get("status") in ["failed", "running-failed"]:
                    return run.get("id")
            return None

        def get_run_logs(self, last_lines: int = 100):
            failed_run_id = self.get_last_failed_run_id()
            response = self.__make_request(
                f"/environments/{self.environment_id}/runs/{failed_run_id}/logs"
            )
            if response.status_code != 200:
                return (f"Failed to get logs for run {failed_run_id}. Status code: {response.status_code}."
                        f"Response: {response.text}")

            return "\n".join(response.text.replace("\\n", "\n").split("\n")[-last_lines:])


    instenv = InstEnvHelper(environment_id)
    env_configuration = instenv.get_environment_configuration()
    last_logs = instenv.get_run_logs()

    print("Environment configuration:")
    print(env_configuration)
    print("Last failed run logs:")
    print(last_logs)


if __name__ == "__main__":
    typer.run(get_instenv_logs)