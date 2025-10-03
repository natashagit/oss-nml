"""Main module for demonstrating the mail client."""

# ta-assignment/main.py

import contextlib
import logging

import gmail_client_impl  # noqa: F401
import mail_client_api
import mail_client_adapter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    """Initialize the client and demonstrate all mail client methods."""

    client = mail_client_adapter.get_client()

    # Test 1: Get messages (existing functionality)
    messages = list(client.get_messages(max_results=3))

    if not messages:
        return

    for i, msg in enumerate(messages, 1):
        print(f'------------- Message {i} -------------')
        print(f"{msg.id}: {msg.subject}")
        print(f"Msg id : {msg.id}")
        print(f"Subject : {msg.subject}")
        print('---------------------------------------')

    # Test 2: Get a specific message by ID
    if messages:
        test_message_id = messages[0].id
        with contextlib.suppress(Exception):
            msg = client.get_message(test_message_id)
            print(f'------------- Message -------------')
            print(f"From : {msg.from_}")
            print(f"Date : {msg.date}")
            print(f"Subject : {msg.subject}")
            print(f"Body :\n{msg.body or '[no body]'}")
            print('------------------------------------')

    # Test 3: Mark a message as read
    if messages:
        test_message_id = messages[0].id
        with contextlib.suppress(Exception):
            success = client.mark_as_read(test_message_id)
            if success:
                print("Message successfully marked as read ✅")
            else:
                print("Failed to mark message as read ❌")

    # Test 4: Delete a message (WARNING: This is destructive!)
    # Only test if we have more than one message to avoid deleting all messages
    if len(messages) > 1:
        # Ask for confirmation before deleting
        delete_message_id = messages[-1].id  # Delete the last message
        try:
            confirmation = input("Type 'DELETE' to confirm deletion: ")
            if confirmation == "DELETE":
                success = client.delete_message(delete_message_id)
                if success:
                    logger.info("Message with ID %s deleted.", delete_message_id)
                else:
                    logger.info("Failed to delete message with ID %s.", delete_message_id)
        except EOFError:
            # This means that CircleCI or another non-interactive environment is not going to actually delete anything
            pass
    else:
        pass

    print("Demo complete.")  # noqa: T201


if __name__ == "__main__":
    main()
