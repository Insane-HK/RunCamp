import os
from dotenv import load_dotenv

load_dotenv()

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
RPC_URL = os.getenv("RPC_URL")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
TOKEN_ADDRESS = os.getenv("TOKEN_ADDRESS", "")

NEYNAR_API_KEY = os.getenv("NEYNAR_API_KEY")
SIGNER_UUID = os.getenv("SIGNER_UUID")