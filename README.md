# A Minimalist CI Pipeline

_This project is currently under development._

This small yet robust self hosted Continuous Integration system can be self-hosted on your server to run tests and monitor the results. It is designed to be simple to understand and easy to extend. Every part of the system is modular and can be replaced / extended with a different implementation. Every function is well documented and easy to understand.

The workflow is the following:

Github sends a webhook notification to the server when a new commit is pushed to the repository. The server then runs the tests and keeps track of the results. The results are then displayed on a web page.

The webhook is secured by a secret token that is shared between Github and the server. This ensures that only authorized users can trigger the pipeline.

See [this](https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries) for more information on how to secure your webhook.