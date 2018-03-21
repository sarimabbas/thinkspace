# Thinkspace
[![CircleCI](https://circleci.com/gh/sarimabbas/thinkspace.svg?style=svg)](https://circleci.com/gh/sarimabbas/thinkspace)<br>
<img src="templates/assets/aaron-2.png" width="250px" alt="Logo"><br>
This repo holds the Thinkspace REST API (and possibly an accompanying web interface).

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

## To-dos:
1. Refactor validators and arguments in separate file
2. Add more convenience methods
3. Rigorous testing

## Basic endpoints

The four basic endpoints are:
1. `/api/users`
2. `/api/users/<int:id>`
3. `/api/projects`
4. `/api/projects/<int:id>`

### 1. /api/users

#### GET

##### Multiple users

By default, the first page of a paginated list of users is returned. To move forward in the pagination, use the following optional arguments:

1. `page` : which page of results to retrieve
2. `per_page` : how many results to show per page

Example:

```bash
curl --request GET \
  --url http://ythinkspace.herokuapp.com/api/v1/users \
  --header 'content-type: application/json' \
  --data '{
	"page": 1,
	"per_page" : 1
}'
```

##### Specific user

To request a specific user, use any one of the following optional arguments:

1. `id`
2. `username`
3. `email`

If any of these arguments are included in the request, multiple users will not be retrieved. A user will be returned if it exists, otherwise an error will be thrown.

Example:

```bash
curl --request GET \
  --url http://ythinkspace.herokuapp.com/api/v1/users \
  --header 'content-type: application/json' \
  --data '{
	"username" : "sarimabbas"
}'
```

Example of error:

```json
{
	"errors": {
		"username": [
			"No user exists with this username."
		]
	}
}
```

#### POST

Create a new user with the following arguments:

1. `username` : required
2. `password` : required
3. `email` : required
4. `first_name` : optional
5. `last_name` : optional

Errors result when
1. An email is malformed
2. A password is not of minimum length
3. A username or email already exists

Upon successful creation, the new user is returned.

Example: 

```bash
curl --request POST \
  --url http://ythinkspace.herokuapp.com/api/v1/users \
  --header 'content-type: application/json' \
  --data '{
	"email" : "john.doe@yale.edu",
	"username" : "johndoe",
	"password" : "hellojohn",
	"first_name" : "John",
	"last_name" : "Doe"
}'
```

### 2. /api/users/<int:id>

#### GET

Get a single user by URL.

Example: 

```bash
curl --request GET \
  --url http://ythinkspace.herokuapp.com/api/v1/users/1 \
  --header 'content-type: application/json'
```

If a user does not exist, an error is returned:

```json
{
	"errors": {
		"id": [
			"No user exists with this id."
		]
	}
}
```

#### PUT 

Update a user's information. Allows for direct manipulation of non-relational properties. To manipulate other properties, use the convenience methods instead. 

Authentication is required for this method. 
1. Use `username` to authenticate
2. Access is for site administrators and users with API write access only

All optional arguments (consult models.py):
1. `first_name`
2. `last_name`
3. `email`
4. `site_admin`
5. `site_curator`
6. `api_write`

Errors will be thrown when:
1. The user making the request was not successfully authenticated
2. The user making the request does not have the necessary privileges/access
3. Updating an email address with one that is already in use

### 3. /api/projects

#### GET

##### Multiple projects

By default, the first page of a paginated list of projects is returned. To move forward in the pagination, use the following optional arguments:

1. `page` : which page of results to retrieve
2. `per_page` : how many results to show per page

##### Specific user

To request a specific projects, use any one of the following optional arguments:

1. `id`

Example:

```bash
curl --request GET \
  --url http://ythinkspace.herokuapp.com/api/v1/projects \
  --header 'content-type: application/json' \
  --data '{
	"id" : "1"
}'
```

Example of error:

```json
{
	"errors": {
		"username": [
			"No project exists with this id."
		]
	}
}
```

#### POST

Create a new project. Authentication is required. Project administrators and members are updated with the creator's information automatically. 

The following arguments are used:
1. `title` : required
2. `subtitle` : optional
3. `description` : optional
4. `tags` : optional, a single tag or list of tags

Example:
```bash
curl --request POST \
  --url http://ythinkspace.herokuapp.com/api/v1/projects \
  --header 'authorization: Basic am9obmRvZTI6aGVsbG9qb2hu' \
  --header 'content-type: application/json' \
  --data '{
	"title" : "Blockchain Coffee",
	"subtitle" : "Using blockchain to track supply of premium coffee beans",
	"tags" : ["Food"]
}'
```

Errors are thrown when:
1. One or more of the tags do not exist
2. The title is not present
3. User is not authenticated

#### PUT 

Update a projects's information. Allows for direct manipulation of non-relational properties. To manipulate other properties, use the convenience methods instead. 

Authentication is required for this method. Access is for:
1. site administrators and users with API write access
2. project admin

All optional arguments (consult models.py):
1. `title` 
2. `subtitle`
3. `description`
For these arguments, new tags/members/admin are appended, old ones are retained.
4. `tags` : a single tag or list of tags
5. `members` : a single username or list of usernames
6. `admin` : a single username or list of usernames

Example:

```bash
curl --request PUT \
  --url http://ythinkspace.herokuapp.com/api/v1/projects/1 \
  --header 'authorization: Basic am9obmRvZTI6aGVsbG9qb2hu' \
  --header 'content-type: application/json' \
  --data '{
	"title" : "New Project Name",
	"tags" : ["Food"],
	"members" : "johndoe"
}'
```

Errors will be thrown when:
1. The user making the request was not successfully authenticated
2. The user making the request does not have the necessary privileges/access
3. Tags, members or admin do not exist

## Other functionality/convenience methods (work in progress)

The idea is to encapsulate most of the logic on the server side so that minimal work is needed on the client side.

### Heart and Unheart

Hearts a user on behalf of the authenticated user

* Authentication: required
* Arguments:
    1. `heartee` : required. The username for the user to heart
* Response: a list of both users with updated heart information
* Errors are thrown when hearting or unhearting the same user multiple times

Example: 

```bash
curl --request POST \
  --url http://ythinkspace.herokuapp.com/api/v1/users/heart \
  --header 'authorization: Basic am9obmRvZTI6aGVsbG9qb2hu' \
  --header 'content-type: application/json' \
  --data '{
	"heartee" : "sarimabbas"
}'
```