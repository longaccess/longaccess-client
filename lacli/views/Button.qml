import QtQuick 1.1

Rectangle {
    id: button

    property alias text: textItem.text
    property bool enabled: false
    property alias radius: button.radius
    property alias font: textItem.font
    signal buttonClicked()

    width: textItem.width + 40; height: textItem.height + 10
    border.width: 1
    radius: height/4
    smooth: true

    gradient: Gradient {
        GradientStop { id: topGrad; position: 0.0; color: "#333" }
        GradientStop { id: bottomGrad; position: 1.0; color: "#000" }
    }

    Text {
        id: textItem
        x: parent.width/2 - width/2; y: parent.height/2 - height/2
        font.pixelSize: 18
        color: "black"
        style: Text.Raised
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        enabled: false
    }

    states: [
    State {
        name: "pressed"; when: mouseArea.pressed && mouseArea.containsMouse
        PropertyChanges { target: topGrad; color: "white" }
        PropertyChanges { target: bottomGrad; color: "white" }
        PropertyChanges { target: textItem; x: textItem.x + 1; y: textItem.y + 1; font.family: "Arial"; explicit: true }
        PropertyChanges { target: mouseArea; enabled: true; onClicked: button.buttonClicked() }
    },
    State {
        name: "Enabled"
        when: button.enabled
        PropertyChanges { target: topGrad; position: 0; color: "white" }
        PropertyChanges { target: bottomGrad; position: 1; color: "white" }
        PropertyChanges { target: mouseArea; enabled: true; onClicked: button.buttonClicked() }
    }
    ]
}
