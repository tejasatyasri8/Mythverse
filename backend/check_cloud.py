from qdrant_client import QdrantClient

client = QdrantClient(
    url="https://7c6c76c8-ca84-4028-bdd7-106d877ed10e.australia-southeast1-0.gcp.cloud.qdrant.io",
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6NzVlM2E1NDgtNDAxNy00YmYwLThhMjMtZGFmMDRmMjRjNmFlIn0.vnXYG0nQ16rPyGV-spB79Oro-52w1NjKr6plFZcGCgI"
)

info = client.get_collection("mythverse")

print("Cloud points:", info.points_count)