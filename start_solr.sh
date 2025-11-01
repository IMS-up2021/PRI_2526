#!/bin/bash

CONTAINER_NAME="my_solr"
CORE_NAME="mycore"
SOLR_PORT=8983
CSV_FILE="final.csv"
SCHEMA_FILE="schema.json"

echo "A iniciar o Solr + Core '$CORE_NAME' ..."

if [ "$(docker ps -aq -f name=^${CONTAINER_NAME}$)" ]; then
  echo "A remover container antigo..."
  docker rm -f $CONTAINER_NAME > /dev/null 2>&1
fi

docker run -d --name $CONTAINER_NAME -p $SOLR_PORT:8983 -v ${PWD}:/data solr:9 solr-precreate $CORE_NAME > /dev/null

echo "A aguardar que o Solr arranque..."
sleep 10

if [ -f "$SCHEMA_FILE" ]; then
  echo "A aplicar schema: $SCHEMA_FILE"
  curl -s -X POST -H 'Content-type:application/json' \
    --data-binary @"$SCHEMA_FILE" \
    "http://localhost:${SOLR_PORT}/solr/${CORE_NAME}/schema"
else
  echo "Nenhum schema.json encontrado — a usar modo schemaless."
fi

if [ -f "$CSV_FILE" ]; then
  echo "A indexar dados de $CSV_FILE ..."
  curl -s -X POST -H 'Content-Type: application/csv' \
    --data-binary @"$CSV_FILE" \
    "http://localhost:${SOLR_PORT}/solr/${CORE_NAME}/update?commit=true"
  echo "Dados indexados com sucesso!"
else
  echo "ERRO: ficheiro CSV '$CSV_FILE' não encontrado!"
  exit 1
fi

echo "Interface Solr disponível em: http://localhost:${SOLR_PORT}"
