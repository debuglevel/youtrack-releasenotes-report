# YouTrack Release Notes Report

Connects to YouTrack and fetches all issues meeting certain criteria. Puts them in a Markdown file and converts it into
a PDF(?) file.

## Run the app to fetch the Markdown stuff

```shell
docker build -t youtrack-release-notes . ; docker run -ti --add-host youtrack.hosts:10.101.33.8 --env-file=environment.prod -v "${PWD}/out.docker:/app/out" youtrack-release-notes
```

## Run pandoc to convert it

Works in PowerShell with WSL1:

```shell
docker build -t youtrack-release-notes . ; docker run -ti -v "${PWD}/out:/data" youtrack-release-notes`
```

```shell
`(docker build -t youtrack-release-notes .) -and (docker run -ti -v "${PWD}/out:/data" youtrack-release-notes)`
```

## CAVEATS

It seems that xhtml2pdf has some issues with `<img>` on Windows. It' s reported working on Linux (-> TODO: just use
Docker?)

## Python development cheat sheet

```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
