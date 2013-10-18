Feature: upload command

    Background: setup the command configuration
        Given the home directory is "/tmp/test"
        And the mock API "longaccessmock"
        And the environment variable "LA_API_URL" is "{api_url}path/to/api"
        And an S3 bucket named "lastage"

    Scenario: I run the command with no arguments
        When I run console script "lacli"
        Then I see "lacli>"

    Scenario: I run the command
        Given the command line arguments "archive -h"
        When I run console script "lacli"
        Then I see "Upload a file to Long Access"

    Scenario: I run the command with a different home
        Given the command line arguments "archive create --home /tmp/whatevah"
        And I have 1 prepared archive
        When I run console script "lacli"
        Then I see "No prepared archives."
