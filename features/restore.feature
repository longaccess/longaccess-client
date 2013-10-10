Feature: restore command

    Background: setup the command configuration
        Given the home directory is "/tmp/test"

    Scenario: I restore without having any available archives
        Given the command line arguments "restore -d /tmp"
        When I run console script "lacli"
        Then I see "No available archive to restore"
