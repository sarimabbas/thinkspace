# Thinkspace

[![CircleCI](https://circleci.com/gh/yalethinkspace/thinkspace-api.svg?style=svg)](https://circleci.com/gh/yalethinkspace/thinkspace-api)

This repo holds the Thinkspace REST API.

## Technologies
* Language: Python 3
* Packages:
    * Flask with these important extensions:
        * Flask-HTTPAuth
        * Flask-SqlAlchemy
    * webargs
    * marshmallow
* Data Storage: Heroku Postgres
* Deployment: Heroku

## API documentation

Currently available at: [thinkspace.docs.apiary.io](http://thinkspace.docs.apiary.io)

## Development

Running the following set of commands will start a local Flask server in debug mode. Flask will use the interactive debugger and reloader by default. As per 1.0 documentation, setting ENV and DEBUG in code is discouraged.

```
cd thinkspace-web
export FLASK_APP=app
export FLASK_ENV=development
flask run
```

## How to contribute

1. Fork the [yalethinkspace/thinkspace-web](https://github.com/yalethinkspace/thinkspace-api) repository. Please see GitHub
   [help on forking](https://help.github.com/articles/fork-a-repo) or use this [direct link](https://github.com/yalethinkspace/thinkspace-api/fork) to fork.
2. Clone your fork to your local machine.
3. Create a new [local branch](https://help.github.com/articles/creating-and-deleting-branches-within-your-repository/).
4. Run tests and make sure your contribution works correctly.
5. Create a [pull request](https://help.github.com/articles/creating-a-pull-request) with details of your new feature, bugfix or other contribution.