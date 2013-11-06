Feature: list capsules command

    Background: setup the command configuration
        Given the home directory is "/tmp/test"
        And the mock API "longaccessmock"
        And the environment variable "LA_API_URL" is "{api_url}path/to/api"
        And the username "test" 
        And the password "test"
        And the API authenticates a test user

    Scenario: I try to login with bad credentials
        Given the API authentication is wrong
        And the command line arguments "-u test -p test login"
        When I run console script "lacli"
        Then I see "authentication failed"

    Scenario: I try to login with bad credentials 2
        Given the API authentication is wrong
        And I store my credentials in "{homedir}/.netrc"
        And the command line arguments "login"
        When I run console script "lacli"
        Then I see "authentication failed"

    Scenario: I try to login with bad credentials 3
        Given the API authentication is wrong
        And I store my credentials in "{homedir}/.netrc"
        And the command line arguments "-i"
        When I run console script "lacli"
        Then I see "lacli> "
        When I type "login"
        Then I see "authentication failed"

    Scenario: I try to login with good credentials
        Given the command line arguments "-u test -p test login"
        When I run console script "lacli"
        Then I see "authentication succesfull"

    Scenario: I try to login with good credentials 2
        Given I store my credentials in "{homedir}/.netrc"
        And the command line arguments "login"
        When I run console script "lacli"
        Then I see "authentication succesfull"
