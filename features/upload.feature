Feature: upload command

    Background: setup the command configuration
        Given the home directory is "/tmp/test"

    Scenario: I run the command
        When I run "laput"
        Then I see "Upload to Long Access"

