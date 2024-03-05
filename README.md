![GitHub stars](https://img.shields.io/github/stars/d3cline/airanch?style=social)
![GitHub forks](https://img.shields.io/github/forks/d3cline/airanch?style=social)
![GitHub issues](https://img.shields.io/github/issues/d3cline/airanch)
![Django](https://img.shields.io/badge/django-%205-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Opalstack API](https://img.shields.io/badge/Opalstack-API-orange.svg)

<p align="center">
  <img src="https://raw.githubusercontent.com/d3cline/airanch/main/icon.webp" alt="Logo" width="200"/>
</p>


# AI Ranch

A Django example project for authenticating many users to many AI endpoints.
Complete with UI. Built with: Django REST Framework, DaisyUI, Tailwind.css, Alpine.js, and [Opalstack](https://opalstack.com/).
All the fixin's to bootstrap your next AI startup.

## Key Features

- **Paywall Ollama.ai and other AI workloads**: Only authenticated owners may access hardware. *Sell the llama.*
- **Template Engine**: Manage many UI templates and hardware nodes. *Skin the llama.* 
- **Secure SSH Tunneling for AI Workloads**: SSH tunneling for secure, efficient access to resources. *Secure the llama.*
- **Integration with Traditional Web Hosting**: Seamlessly integrates with [Opalstack](https://opalstack.com/). *Syndicate the llama.*
- **Full-Scale Support for AI Development**: Support for AI Ranch participants. *Support the llama.*

## How it Works

1. Signup for an [Opalstack](https://opalstack.com/) account.
2. Install AI Ranch as a Django app.
3. Issue an API key.
4. Manage home lab routing objects with AI Ranch.

## Requirements

- [Opalstack account](https://my.opalstack.com/signup)

## Installation

1. Install a 'Django' app using the [Opalstack](https://opalstack.com/) Dashboard.
2. Clone the repo
3. Setup the virtualenv, pip install requirements
4. modify the start/stop scripts to use the correct paths
5. Set the following env vars in the start script

```
export OPALSTACK_API_KEY='APITOKEN123'
export NODE_BASE_DOMAIN_NAME='example.com'
```
