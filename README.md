# Thinkspace
[![CircleCI](https://circleci.com/gh/sarimabbas/thinkspace.svg?style=svg)](https://circleci.com/gh/sarimabbas/thinkspace)<br>
<img src="templates/assets/aaron-2.png" width="250px" alt="Logo"><br>
This repo holds the Thinkspace REST API (and possibly an accompanying web interface).

## Technologies
* Language: Python 3
* Libraries:
    * Flask (a web server) with these important extensions:
        * Flask-Restful
        * Flask-HTTPAuth
    * webargs
    * mongoengine (an ODM for MongoDB)
* Data Storage: MongoDB
* Deployment: Heroku

## REST API usage
Four endpoints are exposed: 
```
/api/users
/api/users/<string:doc_id>
/api/projects
/api/projects/<string:doc_id>
```
### GET (retrieve a document)
`curl -X GET http://ythinkspace.herokuapp.com/api/projects` returns a list of all projects<br>
`curl -X GET http://ythinkspace.herokuapp.com/api/user/5a4eab42af6a234b83365aa7` returns a particular user
### POST (insert a new document)
`curl -X POST -H "Content-Type: application/json" -d '{"title" : "johndoe", "password" : "123", "email" : "john.doe@example.com"}' http://ythinkspace.herokuapp.com/api/users`
### PUT (upsert an existing document)
`curl -X POST -H "Content-Type: application/json" -d '{"title" : "My new project"}' http://ythinkspace.herokuapp.com/api/projects --user johndoe:123`
### DELETE (delete a document)
`curl -X DELETE http://ythinkspace.herokuapp.com/api/user/5a4eab42af6a234b83365aa7 --user johndoe:123`
### Notes:
* Each document (a user or project) has a unique document id (the long string of numbers and letters)
* Some methods require authentication, and are further restricted by user roles (see models and code)
* Using webargs, it is possible to parse and accept URL query, form and JSON data
