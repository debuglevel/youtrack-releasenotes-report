# YouTrack Release Notes Report

Connects to YouTrack and fetches all issues meeting certain criteria. Puts them in a Markdown file and converts it into
various document files.

## Prerequisite
* Assumes there is a custom "Release Notes" field.

## Run the app to fetch the Markdown stuff
This runs the app (fetches issues and writes markdown) and converts it to various document formats afterwards vie `pandoc`.

```shell
docker build -t youtrack-release-notes . ; docker run -ti --add-host youtrack.hosts:10.101.33.8 --env-file=environment.prod -v "${PWD}/out.docker:/app/out" youtrack-release-notes
```

Maybe use this `&&` thing instead for PowerShell:
```shell
`(docker build -t youtrack-release-notes .) -and (docker run -ti -v "${PWD}/out:/data" youtrack-release-notes)`
```

## Python development cheat sheet

```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
