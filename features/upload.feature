Feature: upload command

    Background: setup the command configuration
        Given the home directory is "/tmp/test"
        And the mock API "longaccessmock"
        And the environment variable "LA_API_URL" is "{api_url}path/to/api"

    Scenario: I run the command with no arguments
        When I run console script "laput"
        Then I see "lacli>"

    Scenario: I run the command
        Given the command line arguments "-h"
        When I run console script "laput"
        Then I see "Upload a file to Long Access"

    Scenario: I upload an empty file to an incorrect API url
        Given an empty file "foo"
        And the command line arguments "{foo}"
        And the environment variable "LA_API_URL" is "http://stage.longaccess.com/foobar"
        When I run console script "laput"
        Then I see "error: server not found" 

    Scenario: I upload an empty file to a failing API
        Given an empty file "foo"
        And the command line arguments "{foo}"
        And the API is failing
        When I run console script "laput"
        Then I see "error: the server couldn't fulfill your request"

    Scenario: I upload an empty file
        Given an empty file "foo"
        And the command line arguments "{foo}"
        When I run console script "laput"
        Then I see "done"
