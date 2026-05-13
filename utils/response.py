from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def success_response(data=None, message="成功", code=200):
    return JSONResponse(
        status_code=code,
        content=jsonable_encoder(
            {
                "code": code,
                "message": message,
                "data": data,
            }
        ),
    )


def error_response(message="失败", code=400, data=None, debug=None):
    content = {
        "code": code,
        "message": message,
        "data": data,
    }

    if debug is not None:
        content["debug"] = debug

    return JSONResponse(
        status_code=code,
        content=jsonable_encoder(content),
    )
