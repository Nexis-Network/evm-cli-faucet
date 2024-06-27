# Nexis EVM Faucet Server

This is a simple HTTP server for rate-limited Nexis faucet requests. It validates Ethereum addresses and runs a specified command to transfer tokens to the provided address.

## Features

- Validates Ethereum addresses on Nexis Network.
- Limits requests to one per address every 5 minutes.
- Asynchronously runs the `nexis evm transfer-to-evm` command.
- Supports Cross-Origin Resource Sharing (CORS) for web-based applications.

## Requirements

- Python 3.x
- Nexis command-line tool
