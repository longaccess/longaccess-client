import QtQuick 1.1
FocusScope {
    id: focusScope
    property int fontSize: 12
    property int textBoxWidth: parent.width * 0.8
    property int textBoxHeight: 45
    property alias text: textInput.text
    property alias acceptableInput: textInput.acceptableInput
    property alias font: textInput.font
    property alias inputMask: textInput.inputMask
    signal textChanged(string text)
    width: textBoxWidth
    height: textBoxHeight

    Rectangle {
        width: parent.width
        height: parent.height
        color: "#d7d7d7"
        border.color:"#000000"
        border.width: 3
        radius: 0
        MouseArea {
            anchors.fill: parent
            onClicked: {
                focusScope.focus = true
                textInput.openSoftwareInputPanel()
            }
        }
    }

    MouseArea {
        anchors.fill: parent
        onClicked: {
            focusScope.focus = true
            textInput.openSoftwareInputPanel()
        }
    }

    TextInput {
        id: textInput
        anchors {
            right: parent.right
            rightMargin: 8
            verticalCenter: parent.verticalCenter
        }
        focus: true
        selectByMouse: true
        font.pointSize: fontSize
        onTextChanged: focusScope.textChanged(text)
        anchors.left: parent.left
        anchors.leftMargin: 8
    }

    transitions: [
        Transition {
            from: ''; to: 'hasText'
            NumberAnimation {
                properties: 'opacity'
            }
        },
        Transition {
            from: 'hasText'; to: ''
            NumberAnimation {
                properties: 'opacity'
            }
        }
    ]
}
