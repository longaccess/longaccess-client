Feature: upload command

    Background: setup the command configuration
        Given the home directory is "/tmp/test"

    Scenario: I run the command with no arguments
        When I run console script "laput"
        Then I see "lacli>"

    Scenario: I run the command
        Given the command line arguments "-h"
        When I run console script "laput"
        Then I see "Upload a file to Long Access"
