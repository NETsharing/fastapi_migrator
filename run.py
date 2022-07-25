import uvicorn

from app.settings import server_settings

if __name__ == '__main__':
    uvicorn.run(
        "app.instances:app",
        host=server_settings.server_host,
        port=server_settings.server_port,
        debug=server_settings.debug,
        reload=True,
    )
