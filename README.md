# Flock Agent

Flock is a privacy-preserving fleet management system powered by osquery and the Elastic Stack.

**The goal of Flock is to gain visibility into a fleet of laptops while protecting the privacy of the laptop users. It achieves this by only collecting information needed to inform security decisions, and by not allow the IT team to access arbitrary files, or execute arbitrary code, on the laptops they are monitoring.**

See also the [Flock server](https://github.com/firstlookmedia/flock).

## About Flock Agent

Flock Agent only support macOS, at the moment. It is responsible for installing and configuring osquery, and pushing osquery logs to the Flock gateway. You configure it by providing the gateway URL. If the agent is not already registered, it registers itself with the gateway and stores the authentication token locally.

Flock Agent includes a background daemon which reads the log file created by osqueryd and forwards the data onto the gateway.

Exactly what data gets collected is defined is defined in `osquery.conf`, which is included within the Flock Agent package. We update this config by releasing updates to Flock Agent. **When the user is prompted to install the update, it will explain to them what new information is being collected from their computer.**

To see what information is getting collected, check the [osquery.conf file](/flock_agent/config/osquery.conf). In the future we will expand this to include more complicated queries, like [detecting reverse shells](https://clo.ng/blog/osquery_reverse_shell/).

## Getting started

Flock Agent isn't packaged yet. To install from the source tree, first install Python 3.7 (from python.org, or probably `brew install python@3`). Then install pipenv:

```sh
pip3 install pipenv
```

Install the pip environment:

```sh
pipenv install
```

Run the agent software like this:

```sh
pipenv run ./flock-agent
```

Without any commands, it will check the status of the software managed by Flock Agent.

To automatically install and configure Flock software, use `--install`:

```sh
pipenv run sudo ./flock-agent --install
```

To uninstall all of the Flock software, use `--purge`:

```sh
pipenv run sudo ./flock-agent --purge
```
