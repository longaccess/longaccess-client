Feature: restore command

    Background: setup the command configuration
        Given the home directory is "/tmp/test"

    Scenario: I restore without having any available archives
        Given the command line arguments "restore"
        When I run console script "lacli"
        Then I see "No available archive to restore"

    Scenario: I restore without having any available archives
        Given the command line arguments "restore -o /tmp"
        When I run console script "lacli"
        Then I see "No available archive to restore"
