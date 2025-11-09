import base64
import io

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException

from schemas.image import PyplotCode

image_router = APIRouter()


@image_router.post(
    "/generate-graph",
    summary="Generate diagram using Matplotlib code."
)
async def generate_diagram(payload: PyplotCode):
    print(payload.code)
    image_buffer = io.BytesIO()
    execution_globals = {
        "plt": plt,
        "np": np,
        "pd": pd,
    }

    try:
        exec(payload.code, execution_globals)
        plt.savefig(image_buffer, format="png", bbox_inches="tight")
        image_buffer.seek(0)
        img_bytes = image_buffer.getvalue()
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        return {"image": img_b64}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error executing code: {e}")
    finally:
        plt.close("all")
