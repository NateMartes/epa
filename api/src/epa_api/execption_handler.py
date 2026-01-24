from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the real error internally for the developers (Aiden and Azan)
    print(f"CRITICAL ERROR: {exc}") 
    
    # Send a generic message to the mobile application
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred. Please try again later."},
    )