# chef
Infocentric Design of Systems Project

Computer Helping Eat Food

## Application Setup

# Environment

This README assumes that your machine is appropriately setup 
to run Python scripts via the `python3` CLI, and that you have
the Python package manager installed.

### Install dependencies
* `pip install tkinter`
* `pip install dotenv`
* `pip install neo4j`

## Neo4J

There are two options when setting up the Neo4J database. You can either use a free AuraDB instance, which is cloud-based, but has limited plugin support (found [here](https://neo4j.com/cloud/platform/aura-graph-database/)). Simply create an account and follow the instructions listed on the website, then move on to "Setting Environment Variables")

Or, you can install and initialize a local instance on your machine, which has far more robust plugin support, but is not cloud-located. Simply navigate to [this link](https://neo4j.com/docs/operations-manual/current/installation/) and follow the instructions for your environment.

## Setting Environment Variables

In order for CHEF to query the database properly, you must set up a `.env` file with the correct variables. Create a file named `.env` with the variables as specified below:

```
DB_URI=<localhost:port> (if you are running a local instance), or <provided AuraDB endpoint> (if you are running there)
DB_USER=neo4j (by default)
DB_PASS=<as specified by your instance>
```

When your environment variables are set, run `python3 DAO.py` to populate the DB with the starting data.