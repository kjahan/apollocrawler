# apollocrawler
Apollo crawler service using RMQ

# Dependencies

To run the code you need to setup RabbitMQ and also install pika, requests, and pandas Python libraries.

## Create a virtual environment for your crawling project:

`conda create -n crawler python=3.7.2 anaconda`


## Install all required packages:
`conda install -c conda-forge fbprophet`

`pip install pandas`

`pip install yahoofinancials`

`pip install timeout-decorator`

`pip install requests`

`pip install pika`

`pip install psycopg2`

## Steps to install RMQ in MacOS and starting rabbitmq:

`brew update`

`brew install rabbitmq`

`brew services start rabbitmq`

## Start the Stock pipeline:

## To activate the conda environment, run (for MaxOS run `unset PYTHONPATH`):

`conda activate crawler`


## (step I) start crawling producer for emitting stocks:

`python -m apollocrawler.stock_emitter`


## (step II) start saving model predictions :

`python -m apollocrawler.model_saver`


## (step III) start workers to analyze stocks:

`python -m apollocrawler.stock_worker`


## To deactivate the conda environment, run:
`conda deactivate`

#PGAdmin: p:"pgadmin" and pg db pass: ""