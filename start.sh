#! /bin/bash

rm -rf dist
uv sync  --all-groups
uv export --no-editable --no-emit-project -o requirements.txt > /dev/null
uv build
git pull
sudo docker build . -t imapsync
sudo docker compose pull
sudo docker compose down
sudo docker compose up --remove-orphans -d --build
sudo docker compose logs -f
