import requests

GRAPHQL_URL = "http://localhost:8000/graphql"

query = """
query{
  products{
    id,
    name,
    price,
    stock
  }
}
"""

variables = {"id": 2}

query_with_variables = """
query GetProduct($id: ID!) {
   product(id:$id){
      id,
    	name,
    	price,
    	stock
    }
}
"""

try:
    response = requests.post(
        GRAPHQL_URL,
        json={"query": query_with_variables, "variables": variables},
        headers={"Content-Type": "application/json"}
    )
    
    data = response.json()
    print(data)

except Exception as e:
    print(f"Got an error: {e}")
