Feature: manage certificates command

    Background: setup the command configuration
        Given the home directory is "/tmp/test"
        And an empty folder "tmpfolder" 
        And the Longaccess directory exists in HOME
        And the timeout is 4 seconds

    Scenario: I list available certificates without having any
        Given the command line arguments "certificate list"
        When I run console script "lacli"
        Then I see "No available certificates."

    Scenario: I list available certificates 
        Given the command line arguments "certificate list"
        And I have 1 certificate titled "foobar title"
        When I run console script "lacli"
        Then I see "foobar title"

    Scenario: I export a certificate that doesn't exist
        Given the command line arguments "certificate export doesnotexist"
        When I run console script "lacli"
        Then I see "Certificate not found"

    Scenario: I export a certificate
        Given I have 1 certificate titled "foobar title"
        And the command line arguments "certificate export {certid}"
        And I change to the "{tmpfolder}" directory
        When I run console script "lacli"
        Then I see "longaccess-{certid}.yaml"
        And there is a file "longaccess-{certid}.yaml" under "{cwd}"

    Scenario: I print a certificate that doesn't exist
        Given the command line arguments "certificate print doesnotexist"
        When I run console script "lacli"
        Then I see "Certificate not found"

    Scenario: I export a certificate
        Given I have 1 certificate titled "foobar title"
        And the command line arguments "certificate print {certid}"
        And I change to the "{tmpfolder}" directory
        When I run console script "lacli"
        Then I see "{certid}.html"
        And there is a file "longaccess-{certid}.html" under "{cwd}"

    Scenario: I delete a certificate
        Given I have 1 certificate titled "foobar title"
        And the command line arguments "--batch certificate delete {certid}"
        When I run console script "lacli"
        Then I see "Deleted certificate"

    Scenario: I import a certificate
        Given I have 1 certificate titled "foobar title"
        And the command line arguments "certificate print {certid}"
        And I change to the "{tmpfolder}" directory
        When I run console script "lacli"
        Then I see "longaccess-{certid}.html"
        And there is a file "longaccess-{certid}.html" under "{cwd}"
        Given the command line arguments "--batch certificate delete {certid}"
        When I run console script "lacli"
        Then I see "Deleted certificate"
        Given the command line arguments "certificate import {cwd}/longaccess-{certid}.html"
        When I run console script "lacli"
        Then I see "Imported certificate"
        And there is a file "*.adf" under "{home}/Longaccess/certs"
