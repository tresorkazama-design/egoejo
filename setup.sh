#!/usr/bin/env bash
set -e
echo "Copying example .env -> backend/.env (edit values before running)"
cp backend/.env.example backend/.env || true
echo "Now run: docker-compose up --build"