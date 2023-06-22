run *ARGS: poetry run python -m yutto {{ARGS}}

install: poetry install

fmt: poetry run isort .
    poetry run black .

lint: poetry run pyright src
    poetry run ruff .

clean: find . -name "*.m4s" -print0 | xargs -0 rm -f
    find . -name "*.mp4" -print0 | xargs -0 rm -f
    find . -name "*.mkv" -print0 | xargs -0 rm -f
    find . -name "*.mov" -print0 | xargs -0 rm -f
    find . -name "*.aac" -print0 | xargs -0 rm -f
    find . -name "*.flac" -print0 | xargs -0 rm -f
    find . -name "*.srt" -print0 | xargs -0 rm -f
    find . -name "*.xml" -print0 | xargs -0 rm -f
    find . -name "*.ass" -print0 | xargs -0 rm -f
    find . -name "*.nfo" -print0 | xargs -0 rm -f
    find . -name "*.pb" -print0 | xargs -0 rm -f
    find . -name "*.pyc" -print0 | xargs -0 rm -f
    rm -rf .pytest_cache/
    rm -rf .mypy_cache/
    find . -maxdepth 3 -type d -empty -print0 | xargs -0 -r rm -r
