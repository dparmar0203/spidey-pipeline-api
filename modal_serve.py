import modal

image = (
    modal.Image.debian_slim(python_version="3.13")
    .pip_install(
        "fastapi",
        "uvicorn",
        "pandas",
        "joblib",
        "scikit-learn==1.9.1",
    )
    .add_local_file("pipeline_def.py", "/root/pipeline_def.py")
    .add_local_file("serve.py", "/root/serve.py")
    .add_local_file("pipeline.joblib", "/root/pipeline.joblib")
)

app = modal.App("spidey-pipeline-api")


@app.function(image=image)
@modal.asgi_app()
def fastapi_app():
    from serve import app as web_app

    return web_app
