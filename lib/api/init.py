from . import BaseApi
from fastapi import Request, Response
from fastapi.responses import JSONResponse


class Init(BaseApi):
    def init_api(self):
        self.add_route("/test", self.test, "post")

    async def test(self, request: Request):
        body = await request.body()
        headers = request.headers
        params = request.query_params
        cookies = request.cookies

        response = JSONResponse(
            content={
                "your_body": str(body),
                "your_headers": str(headers),
                "your_params": str(params),
                "your_cookies": str(cookies)
            }
        )
        response.set_cookie("new_cookie", "abcd")
        response.headers["new_header"] = "abcd"

        return response
