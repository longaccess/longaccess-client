Feature: upload command

    Background: setup the command configuration
        Given the home directory is "/tmp/test"
        And the mock API "longaccessmock"
        And the environment variable "LA_API_URL" is "{api_url}path/to/api"
        And an S3 bucket named "lastage"

    Scenario: I run the command interactively
        Given the command line arguments "-i"
        And the Longaccess directory exists in HOME
        When I run console script "lacli"
        Then I see "lacli>"

    Scenario: I run the command interactively with no home
        Given the command line arguments "-i"
        When I run console script "lacli"
        Then I see "~/Longaccess does not exist."
        And I see "Should I create it? (yes/no)"
        When I type "yes"
        Then I see "lacli>"

    Scenario: I run the command
        Given the command line arguments "-h"
        When I run console script "lacli"
        Then I see "Usage:"

    Scenario: I run the command with a different home
        Given the command line arguments "--home {home}/whatevah archive list"
        And I have 1 available archive
        When I run console script "lacli"
        Then I see "{home}/whatevah does not exist"
        And I see "Should I create it? (yes/no)"
        When I type "yes"
        Then I see "No available archives."
