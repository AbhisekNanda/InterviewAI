import asyncio
import websockets
import sys

async def test_websocket(interview_id: int):
    """
    Connects to the WebSocket server, receives an initial message,
    and then enters a loop to continuously send and receive messages.
    """
    # Construct the WebSocket URL from the interview_id
    uri = f"ws://127.0.0.1:8000/ws/extract/{interview_id}"
    print(f"Attempting to connect to: {uri}")

    try:
        # The 'async with' statement handles connection and disconnection automatically.
        async with websockets.connect(uri) as websocket:
            print("Connection successful!")

            # 1. Receive the initial message from the server (the resume text)
            print("\n--- Waiting for server's initial message ---")
            initial_message = await websocket.recv()
            print(f"<<< Received from server:\n{initial_message}")

            # 2. Start a continuous loop to send and receive messages
            print("\n--- Starting continuous message loop (press Ctrl+C to stop) ---")
            message_counter = 0
            while True:
                message_counter += 1
                message_to_send = f"Message #{message_counter} from Python client."

                print(f"\n>>> Sending: '{message_to_send}'")
                await websocket.send(message_to_send)

                # Wait for the echo back from the server
                received_message = await websocket.recv()
                print(f"<<< Received: {received_message}")

                # Wait for 2 seconds before sending the next message
                await asyncio.sleep(2)

    except websockets.exceptions.ConnectionClosed as e:
        print(f"\n[INFO] Connection closed gracefully. Code: {e.code}, Reason: {e.reason}")
    except ConnectionRefusedError:
        print("\n[ERROR] Connection refused. Is the server running?")
        print("This could also be a firewall issue.")
    except KeyboardInterrupt:
        print("\n[INFO] Loop stopped by user (Ctrl+C).")
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Check if an interview_id was provided as a command-line argument
    if len(sys.argv) > 1:
        try:
            interview_id_to_test = int(sys.argv[1])
            # Run the asynchronous function
            asyncio.run(test_websocket(interview_id_to_test))
        except ValueError:
            print("Error: Please provide a valid integer for the interview_id.")
    else:
        print("Usage: python test_client.py <interview_id>")
        print("Example: python test_client.py 1")

