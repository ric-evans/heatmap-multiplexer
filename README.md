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
This was built and tested with Python 3.8.

### Requirements
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

## User Instructions
The app is designed to be extremely interactive. A dataset is preloaded describing the 2001-2015 NBA Drafts. Choose X and Y Dimensions however you'd like, along with any additional binning settings. Everything will load in real time--there is no "compile" button. Naturally, the higher the number of dimensions (and data points) the longer it will take to process. Toggling the visibility switches will allow you to exclude dimensions without losing your binning settings. Using the up/down buttons will render different hierarchies within the heatmap. The heatmap has out-of-the-box interactions like zooming and tooltips.

### Example Configurations
_A single example will produce several examples because each step is rendered in real time._

#### Dataset: `nba-draft-2015.csv` (preloaded)
##### Y Dimensions
1. _Draft_year_ (with default 15 "smart bins")
##### X Dimensions
1. _Position_ (this is categorical)
2. _Bust_ (with default 8 "smart bins")
##### Data Coloring
- Dimensional Statistic
    - _Role Player_
    - Median
