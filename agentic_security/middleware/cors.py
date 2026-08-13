from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        # Credentialed CORS cannot safely be combined with a wildcard origin.
        # The application does not use cookie-based authentication, so keep
        # cross-origin API access while preventing credential reflection.
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
