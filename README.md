# heatmap-multiplexer
A Web App for Building and Interacting with Multi-Variate Heatmaps


## Getting Started

### 1. Set Up Environment
    python3.8 -m virtualenv -p python3.8 env-heatmulti-web
    . env-heatmulti-web/bin/activate
    pip install -r web_app/requirements.txt

### 2. Start the Server
    python -m web_app

### 3. View Webpage
Go to http://localhost:8050/

## Libraries and Tools Used
*(These are also included in the `requirements.txt`)*

- dash (v. 2.0.0)
    - plotly is a dependency
- dash-bootstrap-components (v. 1.0.1)
    - supplementary dash library
- dash-daq (v. 0.5.0)
    - supplementary dash library
- pandas (v. 1.3.4)
    - stats library
- visdcc (v. 0.0.40)
    - additional JavaScript wrapping library
- coloredlogs (v. 15.0.1)
    - for nice looking logs :)
