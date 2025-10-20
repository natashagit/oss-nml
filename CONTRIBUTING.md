## What this project is

The basic idea behind the projec tis that we keep one stable mail-client interface and plug different providers behind it. Your app talks to the interface. Providers can be swapped without touching app code.

## Architecture

Now we split things into two parts: 
1. We have an interface package that defines the client and message contracts
2. A Gmail package that implements the contract and registers itself on import. 

Two parts is needed for loose coupling and easy replacement. Add Outlook or IMAP by wiring in a new provider.

## Design principles

Here we keep interfaces small and stable, while the messy bits (auth, retries, parsing) live inside implementations. Prefer changes inside implementations. Only expand the interface when it is truly necessary, and document it so all providers can follow.

## Repository layout

Each package has its own source, tests, and config. Docs live under docs/. The root config standardizes tools and rules. Keep package initializers light: do the registration there and little else. Use clear, absolute imports so navigation stays easy.

## Testing

Think test pyramid: many fast unit tests that mock external calls, some integration tests that check wiring and registration, and a few end-to-end flows. Aim for strong coverage and test behavior, not internals. Here we name tests so intent is obvious.

## Development workflow

As you work, run the formatter, linter, type checks, and tests. Add unit tests near your change. Add an integration test if it crosses package boundaries. Keep public surfaces small. Now and then, skim the docs to ensure they still match reality.

## Documentation

Write practical Markdown. Treat tests as executable examples, and docs as the story. When behavior or interfaces change, update the docs in the same pull request. Future you will thank present you.

## Continuous integration

Every push runs formatting, linting, typing, and unit tests with coverage. Some integration tests that need credentials run only in trusted contexts. Match your local commands to CI so results do not surprise you.

## Getting started: quick steps (Follow the readMe for more concise steps)

- Clone the repo. Here we pull the code locally so you can work on it. 

- Install the workspace and dev tools. Now we set up dependencies and tooling.

- Run the tests to verify your setup end to end.

- Set environment variables if you will run provider-backed tests (configure credentials first).

- Create a feature branch for your change.

- Start small with a thin, reviewable slice.

## Pull requests

One focused change per PR feels best. Follow the existing style and layout. Include tests and any doc updates. Never commit secrets. If your change affects the interface, call that out in the PR description.
The format for Pull Requests is  given as default when you try to add a PR. Please adhere to it.

## Troubleshooting

If imports feel odd, check that you are running inside the workspace and not from raw source folders. If a provider is not taking effect, make sure its package registers on import. For auth failures in integration tests, recheck environment variables and tokens. If local and CI results differ, run the same commands and do not skip slow tests.

## Questions: quick checklist

- Check the docs and tests first. Often the answer is already there.

- Open a small issue if it is still unclear. Say what you tried, expected, and saw.

- Propose a doc tweak when you spot confusion so we fix it at the source.

- Link the lines or files you are asking about to keep the discussion focused.

- Keep scope narrow so maintainers can help quickly.