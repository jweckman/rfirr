# Default port is 5001, could be something else
curl -X POST http://<HOST>:5001 -d '{"jsonrpc": "2.0", "method": "start_irrigation", "id": 1}'
