tinymce.init({
    selector: '#comment_content'
})

// trying to use as little jQuery as possible
$(document).ready(function () {
    
    $("#comment_form").submit(function (event) {
        // prevent regular form submission
        event.preventDefault()

        // get the comment content and project to make a comment for
        let comment_content = tinyMCE.get("comment_content").getContent()
        let project_id = $(this).data("project-id")
        
        // prepare payload
        let form = new FormData()
        form.append("content", comment_content)
        form.append("project", project_id)

        // create settings to POST
        var settings = {
            "async": true,
            "crossDomain": true,
            "url": "/api/v1/comments",
            "method": "POST",
            "headers": {
                "authorization": "Basic am9obmRvZTI6aGVsbG9qb2hu"
            },
            "processData": false,
            "contentType": false,
            "mimeType": "multipart/form-data",
            "data": form
        }

        // create comment
        $.ajax(settings).done(function (response) {
            console.log(response)
            comment = JSON.parse(response)
            let timestamp = timeago(comment.timestamp)
            let comment_html = 
            "<div class='card' data-comment-id=" + comment.id + ">\
                <div class='card-body'>\
                    <h5 class='card-title'>" + comment.user.first_name + " " + comment.user.last_name + "</h5>\
                    <h6 class='card-subtitle mb-2 text-muted'>" + comment.user.username + "</h6>\
                    <p class='card-text'>" + comment.content + "</p>\
                    <p class='card-text'><small class='text-muted'>" + timestamp.format() + "</small></p>\
                </div>\
            </div>\
            <br>"
            $("#comment-list").prepend(comment_html)
        })

        // prevent regular form submission
        return false
    })


    // I would've called it createComment() but that's already taken
    // async function postComment() {
    //     console.log("entered")
    //     // read our JSON
    //     let response = await fetch('/api/v1/projects')
    //     let projects = await response.json()

    //     console.log("async/await based")
    //     console.log(projects)
    // }
})
