import os
from supabase import create_client, Client
from supabase.client import ClientOptions
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if url is None or key is None:
        raise EnvironmentError(
            "SUPABASE_URL and SUPABASE_KEY environment variables must be set"
        )
    supabase: Client = create_client(
        url,
        key,
        options=ClientOptions(
            postgrest_client_timeout=10,
            storage_client_timeout=10,
            schema="public",
        ),
    )

    response = supabase.table("subscriptions").select("*").execute()

    if not hasattr(response, "data") or len(response.data) == 0:  # type: ignore
        print(f"Credenciais não encontradas para o id: {id}")
        raise ValueError(f"Credenciais não encontradas para o id: {id}")

    data = pd.DataFrame(response.data)  # type: ignore

    

