# Thinkspace

This repo holds the Thinkspace REST API.

## Technologies
* Language: Python 3
* Framework: Django with Django Rest Framework
* Data Storage: Heroku Postgres
* Deployment: Heroku

## API documentation

Currently available at: [thinkspace-api.herokuapp.com/docs](http://thinkspace-api.herokuapp.com/docs)

## Development

Stores media files locally.

```
python manage.py migrate --settings=thinkspace_api.settings.development
python manage.py runserver --settings=thinkspace_api.settings.development
```

## Production

```
python manage.py migrate --settings=thinkspace_api.settings.production
git push heroku master
```

Alternatively you can `git push origin master` and it will auto-deploy to Heroku.

## How to contribute

1. Fork the [yalethinkspace/thinkspace-web](https://github.com/yalethinkspace/thinkspace-api) repository. Please see GitHub
   [help on forking](https://help.github.com/articles/fork-a-repo) or use this [direct link](https://github.com/yalethinkspace/thinkspace-api/fork) to fork.
2. Clone your fork to your local machine.
3. Create a new [local branch](https://help.github.com/articles/creating-and-deleting-branches-within-your-repository/).
4. Run tests and make sure your contribution works correctly.
5. Create a [pull request](https://help.github.com/articles/creating-a-pull-request) with details of your new feature, bugfix or other contribution.