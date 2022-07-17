from fastapi import FastAPI, Request, Response, status
import fastapi
import beta_version2
app = FastAPI()


@app.get('/', status_code=200)
def render_machines(request: Request, response: Response):
    try:
        render_machines.list_of_sorted_machines = beta_version2.sort_machines()
        response.status_code = status.HTTP_200_OK
    except:
        response.status_code = status.HTTP_404_NOT_FOUND
    return render_machines.list_of_sorted_machines


@app.get('/{machine_name}', status_code=200)
def fetch_machine(machine_name: str, request: Request, response: Response):
    for machine in render_machines.list_of_sorted_machines:
        try:
            if machine['name'] == machine_name:
                response.status_code = status.HTTP_200_OK
                return machine
        except:
            response.status_code = status.HTTP_404_NOT_FOUND
