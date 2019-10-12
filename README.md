# apollocrawler
Apollo crawler service using RMQ

## Dependencies

To run the code you need to setup RabbitMQ and also install pika, requests, and pandas Python libraries.

## Create a virtual environment for your crawling project:

`conda create -n crawler python=3.7.2 anaconda`


## Activate this environment, run:

`conda activate crawler`

## Install all required packages:
`conda install -c conda-forge fbprophet`

`pip install pandas`

`pip install yahoofinancials`

`pip install timeout-decorator`

`pip install requests`

`pip install pika`

`pip install psycopg2`

# Steps to install RMQ in MacOS and starting rabbitmq:

`brew update`

`brew install rabbitmq`

`brew services start rabbitmq`

# Start the crawling producer and workers:

`python -m apollocrawler.stock_emitter`

`python -m apollocrawler.stock_worker`


# To deactivate the conda environment, run:
`conda deactivate`