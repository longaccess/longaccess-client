Feature: prepare archive command

    Background: setup the command configuration
        Given the home directory is "/tmp/test"
        And the Longaccess directory exists in HOME

    Scenario: I list available archives without having any
        Given the command line arguments "archive list"
        When I run console script "lacli"
        Then I see "No available archives."

    Scenario: I list available archives
        Given the command line arguments "archive list"
        And I have 1 available archive titled "foobar title"
        When I run console script "lacli"
        Then I see "foobar title"

    Scenario: I list available archives with title
        Given the command line arguments "archive list"
        And I have 1 available archive titled "foobar title"
        When I run console script "lacli"
        And I see "foobar title"

    Scenario: I prepare a new archive but give a non-existent directory
        Given the command line arguments "archive create -t foo doesnotexistdir"
        When I run console script "lacli"
        Then I see "The specified folder does not exist"

    Scenario: I prepare a new archive with an empty directory
        Given an empty folder "foo"
        And the command line arguments "archive create -t foo {foo}"
        When I run console script "lacli"
        Then I see "archive prepared"

    Scenario: I prepare a new archive with an empty directory and title
        Given an empty folder "foo"
        And the command line arguments "archive create -t foo {foo}"
        When I run console script "lacli"
        Then I see "archive prepared"
        And there is an archive titled "foo"

    Scenario: I prepare a new archive but it fails due to unreadable files
        Given an empty folder "foo"
        And under "{foo}" an empty file "bar"
        And file "{bar}" is unreadable
        And the command line arguments "archive create -t foo {foo}"
        When I run console script "lacli"
        Then I see "error: "

    Scenario: I prepare a new archive but it fails due to unwritable files
        Given an empty folder "foo"
        And an empty folder "bar"
        And directory "{bar}" is unwritable
        And the command line arguments "--home {bar} archive create -t foo {foo}"
        When I run console script "lacli"
        Then I see "error: "
