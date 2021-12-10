# Create a Knowledge Graph using Corpus from Wikipedia

## To setup the database Neo4j type the command

```text
docker-compose up
```

This will start pull the docker image from docker hub and start the database at port 7474. So the database URL is: `http://localhost:7474`. Credentials for the database.

```text
username: neo4j
password: kgDemo
```

Save these credentials in a `.py` file and name that file `config.py`. These credentials can be changed from the docker-compose.yml file. Now to install the necessary packages run the command: `pip install -r requirements.txt`. It's better to use virtual environment to install the packages.

Spacy model is needed to tokenize texts. To download the model, run the command: 

```python
python3 -m spacy download en_core_web_md
```

To get an initial corpus of wikipedia run the script `build_corpus.py`. This will download the corpus from wikipedia and save it in a `corpus.txt` file. The corpus topics can be changed in the file `build_corpus.py` to get wikipedia summary for preferred pages.

To use the **Google Knowledge Graph API** we will need to create a project in Google Cloud Platform and get an API. The API is free and can be used for a limited number of requests (100,000 Per day). The instructions can be found [here](https://developers.google.com/knowledge-graph/prereqs).

Paste the API key in a file and name it `api_key` and put it in the parent directory.

Now to start processing the corpus and build the knowledge graph run the file `main.py`.

This will take quite some time as this file cleans the text, tokenizes them, removes stop words, stems them and creates the nodes and edges in the database. After the file run is complete we can visualize the graph in Neo4j.

To watch all the nodes with all the connections run the command:

```cypher
MATCH (n) RETURN n
```

To watch all the nodes connected to a node run the command:

```cypher
MATCH (n:Node {name: "<a node name>"}) -- (m:Node) return m.name
```
