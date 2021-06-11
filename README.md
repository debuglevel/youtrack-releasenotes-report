
## CAVEATS
It seems that xhtml2pdf has some issues with `<img>` on Windows. It' 
s reported working on Linux (-> TODO: just use Docker?)

## Python development cheat sheet

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## pandoc Docker
Works in PowerShell with WSL1:
`docker build -t youtrack-release-notes . ; docker run -ti -v "${PWD}/out:/data" youtrack-release-notes`
`(docker build -t youtrack-release-notes .) -and (docker run -ti -v "${PWD}/out:/data" youtrack-release-notes)`