# rock-paper-scissors-sockets
A web app for playing rock paper scissors built with FastApi and Elm using WebSockets

# Setup
## Backend
Create a virtual environment and run (in the root directory)
```
pip install -r app/requirements.txt
pip install uvicorn[standard]
uvicorn app.main:app --reload
```
## Frontend
In the `frontend` directory run
```
npx elm-live -p 8080 -- src/Main.elm --output elm.js
```
(it's necessary to specify a port, since both uvicorn and elm-live use 8000 by default)
or
```
elm make src/Main.elm --output elm.js
```
