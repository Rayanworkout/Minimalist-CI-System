# A Minimalist CI Pipeline

_This project is currently under development._

This project is a minimalist CI system that you can deploy on your server to run tests and deploy your code. It is designed to be simple to understand and easy to extend.

The workflow is the following:

Github sends a webhook notification to the server when a new commit is pushed to the repository. The server then runs the tests and builds the code if the tests pass.

The webhook is secured by a secret token that is shared between Github and the server. This ensures that only authorized users can trigger the pipeline.

See [this](https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries) for more information on how to secure your webhook.