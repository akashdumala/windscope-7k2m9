# WindScope — UK Wind Generation Forecast Analytics

WindScope compares UK wind generation forecasts against actual generation for January 2026. It calculates forecast error metrics and visualises hourly actual and forecast generation.

## Features

- Actual wind generation from the Elexon FUELHH dataset, filtered to `WIND`
- Forecast generation from the Elexon WINDFOR dataset
- Hourly comparison of forecast values against actual values
- Mean Absolute Error (MAE), Root Mean Square Error (RMSE), and forecast bias
- Data coverage and analysis details
- React dashboard and Python Flask API
- Docker Compose setup

## Technology Stack

- Frontend: React, Vite, Recharts
- Backend: Python, Flask, Requests
- Data source: Elexon BMRS API
- Deployment packaging: Docker, Docker Compose

## Project Structure

```text
wind-forecast-analyzer/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── elexon.py
│   │   ├── routes.py
│   │   └── services.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── run.py
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
├── .gitignore
└── README.md
```

## Run with Docker

Prerequisites: Docker Desktop installed and running.

From the project root, run:

```bash
docker compose up --build
```

Open the frontend at:

http://localhost:5173

The backend API is available at:

- Health check: http://localhost:5000/api/health
- January 2026 analysis: http://localhost:5000/api/analysis/january-2026

Stop the application with `Ctrl+C`. To stop containers started in detached mode, run `docker compose down`.

## Metrics

- **MAE:** Average absolute difference between forecast and actual generation.
- **RMSE:** Square root of the average squared forecast error; larger errors receive more weight.
- **Forecast bias:** Average forecast minus actual generation. Positive values indicate overforecasting.

## Evaluation Assumptions and Limitations

The analysis aggregates two half-hourly actual generation readings into an hourly average to compare with hourly forecasts.

The 12:00 UTC previous-day forecast publication cutoff is an illustrative assumption, not a confirmed purchasing deadline. Metrics should be interpreted in light of this assumption and the data coverage returned by the API.

## Data Source

Elexon BMRS API datasets:

- FUELHH — half-hourly generation by fuel type
- WINDFOR — wind generation forecasts

API documentation: https://bmrs.elexon.co.uk/api-documentation

## AI Assistance

ChatGPT was used to assist with implementation, debugging, and documentation. The project was tested locally using Docker Compose.

## Deployment

Public application URL: To be added after deployment.

GitHub repository URL: To be added after publishing.
