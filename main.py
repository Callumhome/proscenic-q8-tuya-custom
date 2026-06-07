from fastapi import FastAPI, HTTPException
from services.robot_service import robot_service

app = FastAPI()

@app.get("/robot/clean/{room}")
def clean_room(room: str):
    response = robot_service.clean_room(room)
    if not response.get("success", False) and "error" in response:
         # Tuya SDK sometimes returns success: True even on failures, check response structure details if needed
         # But basic check:
         if response.get("code"): # Tuya error code present
             raise HTTPException(status_code=500, detail=response)

    return response

@app.get("/robot/stop")
def return_to_base():
    response = robot_service.return_to_base()
    if not response.get("success", False) and "error" in response:
         # Tuya SDK sometimes returns success: True even on failures, check response structure details if needed
         # But basic check:
         if response.get("code"): # Tuya error code present
             raise HTTPException(status_code=500, detail=response)

    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8111)