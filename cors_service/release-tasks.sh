#!/bin/bash

echo "Running Release Tasks"

echo "Running Migrations"
make migrate

echo "Done"