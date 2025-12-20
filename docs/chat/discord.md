# Discord Chat Integration

The chat layer uses the shared `chat_client_api` contract with a Discord implementation.
The AI Ticket service posts responses to a channel after executing ticket actions.

Required environment variables:
- `DISCORD_BOT_TOKEN`
- `CHAT_CHANNEL_ID` (or `DISCORD_CHANNEL_ID`)

Optional:
- `DISCORD_DEFAULT_TOKEN_TYPE` (default `Bot`)
- `CHAT_SYSTEM_PROMPT`
- `CHAT_USER_ID`

Tip: use `/chat/command` in the AI Ticket service to trigger a post to the channel.
