Feature: upload command

    Background: setup the command configuration
        Given the home directory is "/tmp/test"
        And the mock API "longaccessmock"
        And the environment variable "LA_API_URL" is "{api_url}path/to/api"
        And an S3 bucket named "lastage"

    Scenario: I try an upload without files
        Given the command line arguments "put"
        When I run console script "lacli"
        Then I see "Usage:"

    Scenario: I upload an empty file to an incorrect API url
        Given an empty file "foo"
        And the command line arguments "put {foo}"
        And the environment variable "LA_API_URL" is "http://stage.longaccess.com/foobar"
        When I run console script "lacli"
        Then I see "error: server not found" 

    Scenario: I upload an empty file to a failing API
        Given an empty file "foo"
        And the command line arguments "put {foo}"
        And the API is failing
        When I run console script "lacli"
        Then I see "error: the server couldn't fulfill your request"

    Scenario: I upload an non-existent file
        Given the command line arguments "put /tmp/thisdoesnotexist"
        When I run console script "lacli"
        Then I see "File /tmp/thisdoesnotexist not found."


    Scenario: I upload an empty file
        Given an empty file "foo"
        And the command line arguments "put {foo}"
        When I run console script "lacli"
        Then I see "done"

    Scenario: I upload a small file
        Given a file "foo" with contents
        """
            The quick brown fox, ah whatever.
        """
        And the command line arguments "put {foo}"
        When I run console script "lacli"
        Then I see "done"
