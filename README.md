# apollocrawler
Apollo crawler service using RMQ

## Dependencies

To run the code you need to setup RabbitMQ and also install pika, requests, and pandas Python libraries.

## Create a virtual environment for your crawling project:

`conda create -n crawler python=3.7.2 anaconda`


## Activate this environment, run:

`conda activate crawler`

# MaxOS:

`unset PYTHONPATH`


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

## Start the Stock pipeline:

# Start crawling producer (emitting stocks):

`python -m apollocrawler.stock_emitter`


# Start crawling producer (analyzing stocks):

`python -m apollocrawler.stock_worker`


 # Start saving models stats:

`python -m apollocrawler.model_saver`

# To deactivate the conda environment, run:
`conda deactivate`

#PGAdmin: p:"pgadmin" and pg db pass: ""