# BITS Course Repository

Personal learning repository for BITS (Birla Institute of Technology and Science) coursework, including assignments, labs, and mini-projects across APIs, data engineering, cloud economics, and distributed/parallel systems.

## What You Will Find

This repository is organized by course/module folder. Each folder usually contains:
- implementation code
- experiment scripts
- lab artifacts
- course-specific datasets or outputs

## Repository Structure

### [`API Assignment 2`](API%20Assignment%202/)
- `app_final.py`: final API application
- `Assignemnt_2_Rag/`: RAG (Retrieval-Augmented Generation) implementation
  - `app.py`, `config.py`, `rag.py`: core application logic
  - `test_answer_output.py`, `test_rag.py`: test scripts
  - `chroma_data/`: Chroma vector database data
  - `documents/`: source documents for retrieval

### [`API_Assignment_1`](API_Assignment_1/)
- `DataOps/`: data operations and analysis modules
  - includes stats, binning, EDA, encoding, normalization, correlation, and visualization scripts
- `MLOps-MLFlow/`: MLflow-based MLOps workflow
  - `main.py`: pipeline entry point
- `Prefect/`: Prefect-based workflow automation
  - `api/`: deployment and API-related files
  - `tasks/`: reusable task modules
  - `flows/`: workflow definitions

### [`BDS`](BDS/)
- NoSQL/database operation scripts
  - CRUD: `create.py`, `read.py`, `update.py`, `delete.py`
  - utilities: `consistency.py`, `import_json.py`
  - sample data: `ecommerce_data.json`

### [`CISS`](CISS/)
- concurrent and distributed systems exercises
  - `hello_world.c`: basic C program
  - `matrix_multiplication.py`: matrix multiplication
  - `vector_addition.cu`: CUDA vector addition
  - `sequential.py`, `parallel.py`: sequential vs parallel comparison

### [`Cloud Economics`](Cloud%20Economics/)
- `aws_billing_seed.sh`: AWS billing and cloud cost seed/setup script

### [`DS`](DS/)
- distributed systems implementation
  - `chat_server.py`: chat server
  - `client_node.py`: client node
  - `dme_middleware.py`: middleware layer

### [`DS-LAB1`](DS-LAB1/)
- distributed systems lab exercises
  - Python and C client/server implementations
  - `server1.py`, `server2.py`: server variants
  - `client.py`, `client.c`: client variants
  - `docker-compose.yml`: container orchestration for lab setup

### [`PDS`](PDS/)
- parallel and distributed systems programming practice
  - MPI examples: `mpi_example.c`, `mpi_example_2.c`, `mpi_example_non.c`
  - OpenMP: `omp.c`
  - threading and synchronization: `threading.c`, `mutex.c`, `semaphore.c`
  - algorithm/programming exercises: `sum.c`, `multiply.c`, `sort.c`, etc.

## Tech Stack (Across Modules)

- Languages: Python, C, C++, CUDA
- Frameworks/Tools: FastAPI, Prefect, MLflow
- Data/Storage: Chroma, SQLite, JSON-based datasets
- Cloud: AWS
- Parallel Computing: MPI, OpenMP, CUDA
- Containers: Docker

## Getting Started

1. Clone the repository:
   - `git clone <repo-url>`
2. Open the folder and move to the module you want:
   - `cd "API_Assignment_1"` (example)
3. Check the module files and local instructions (if present).
4. Install dependencies for that module (for Python modules, usually via `requirements.txt`).
5. Run scripts from inside that module folder.

## Suggested Workflow

- Keep each course/module independent when installing dependencies.
- Use virtual environments for Python-based assignments.
- Treat generated output folders as artifacts unless explicitly required in submissions.

## License

This repository is maintained for educational and academic purposes.