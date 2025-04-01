# NYU DevOps Project Template

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)
[![CI](https://github.com/CSCI-GA-2820-SP25-003/inventory/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-SP25-003/inventory/actions)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-SP25-003/inventory/branch/main/graph/badge.svg)](https://codecov.io/gh/CSCI-GA-2820-SP25-003/inventory)

## Manual Setup

There are 4 hidden files that you will need to copy manually if you use the Mac Finder or Windows Explorer to copy files from this folder into your repo folder.

These should be copied using a bash shell as follows:

```bash
    cp .gitignore  ../<your_repo_folder>/
    cp .flaskenv ../<your_repo_folder>/
    cp .gitattributes ../<your_repo_folder>/
```

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
pyproject.toml      - Poetry list of Python libraries required by your code

service/                   - service python package
├── __init__.py            - package initializer
├── config.py              - configuration parameters
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── cli_commands.py    - Flask command to recreate all tables
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/                     - test cases package
├── __init__.py            - package initializer
├── factories.py           - Factory for testing with fake objects
├── test_cli_commands.py   - test suite for the CLI
├── test_models.py         - test suite for business models
└── test_routes.py         - test suite for service routes
```

## Inventory Microservice Overview

This microservice is responsible for managing inventory in an eCommerce website. It follows RESTful API principles and supports CRUD operations for inventory items.

### Features

- Create a new inventory item
- Read details of an inventory item
- Update an inventory item
- Delete an inventory item
- List all inventory items

### Installation & Setup

#### Prerequisites

- Install Docker
  
- Install VS Code with the DevContainers extension
  
#### Running the Project

- Clone this repository:
  
   ```bash
   git clone https://github.com/CSCI-GA-2820-SP25-003/inventory.git
   cd inventory

- Open the project in VS Code.
  
- When prompted, reopen in a DevContainer.


### API Endpoints

- **GET** `/inventory`  
  List all inventory items.

- **POST** `/inventory/`  
  Create a new inventory item.

- **GET** `/inventory/{id}`  
  Retrieve a specific inventory item by ID.

- **PUT** `/inventory/{id}`  
  Update a specific inventory item by ID.

- **DELETE** `/inventory/{id}`  
  Delete a specific inventory item by ID.

### Enhanced Query Parameters

- **GET** `/inventory?name=ItemName`  
  Filter inventory by item name.

- **GET** `/inventory?product_id=123`  
  Filter inventory by product ID.

- **GET** `/inventory?condition=New`  
  Filter inventory by condition (`New`, `Used`, etc.).

- **GET** `/inventory?below_restock_level=true`  
  Retrieve only inventory items that are below their restock level.

## Usage Examples with `curl`

### Create a new inventory item

```bash
curl -X POST http://localhost:8080/inventory \
     -H "Content-Type: application/json" \
     -d '{
           "name": "Laptop",
           "product_id": 1001,
           "quantity": 4,
           "condition": "New",
           "restock_level": 5
         }'
```

### List all inventory items

```bash
curl http://localhost:8080/inventory
```

### Get a specific inventory item by ID

```bash
curl http://localhost:8080/inventory/1
```

### Update an inventory item:

```bash
curl -X PUT http://localhost:8080/inventory/1 \
     -H "Content-Type: application/json" \
     -d '{
           "name": "UpdatedName",
           "product_id": 1001,
           "quantity": 8,
           "condition": "Used",
           "restock_level": 3
         }'
```

### Delete an inventory item

```bash
curl -X DELETE http://localhost:8080/inventory/1
```

## Enhanced Feature Examples

### Find items below their restock level

```bash
curl http://localhost:8080/inventory?below_restock_level=true
```

### Filter inventory by name

```bash
curl http://localhost:8080/inventory?name=Laptop
```

### Filter inventory by condition

```bash
curl http://localhost:8080/inventory?condition=Used
```

### Filter inventory by product_id

```bash
curl http://localhost:8080/inventory?product_id=1001
```

## Running Tests

Tests can be run using pytest through the Makefile from within the container: make install make test

## Kubernetes Local Development Commands

Initialize the Cluster

```text
make cluster
```

Map the cluster-registry to 127.0.0.1

```text
sudo bash -c "echo '127.0.0.1 cluster-registry' >> /etc/hosts"
```

Build and Push the Docker Image

```text
# Build Docker image
docker build -t inventory:1.0 .

# Tag it for the local cluster registry
docker tag inventory:1.0 cluster-registry:5000/nyu-devops/inventory:1.0.0

# Push the image to the local registry
docker push cluster-registry:5000/nyu-devops/inventory:1.0.0
```

Deploy PostgreSQL and the Microservice

```text
# Apply PostgreSQL manifests
kubectl apply -f k8s/postgres/pv.yaml
kubectl apply -f k8s/postgres/secret.yaml
kubectl apply -f k8s/postgres/statefulset.yaml
kubectl apply -f k8s/postgres/pvc.yaml
kubectl apply -f k8s/postgres/service.yaml

# Apply inventory microservice manifests
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

Verify the Deployment

```text
kubectl get all
kubectl get pods
kubectl get ingress
```

After resources have been deployed, test that the microservice is running by accessing the /health endpoint.

```text
# Port-forward to test the /health endpoint
kubectl port-forward svc/inventory 8080:8080

#If port 8080 is already in use on your system, use a different local port (e.g. 8081):
kubectl port-forward svc/inventory 8081:8080

# In a new terminal or tab:
curl http://localhost:8080/health
```

Make sure  ingress.yaml correctly routes /health to the inventory service on port 8080

Expected Output:

```text
{ "status": "OK" }
```

Cleanup Commands:

```text
kubectl delete -f k8s/postgres/
kubectl delete -f k8s/
make cluster-rm
```

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
