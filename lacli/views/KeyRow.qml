import QtQuick 1.1


FocusScope {
    id: rect
    property bool complete: false
    property bool acceptable: textbox.acceptableInput
    signal rowChanged(string val)
    width: childrenRect.width
    height: childrenRect.height

    Row {
        id: row1
        layoutDirection: Qt.RightToLeft
        spacing: 0

        Rectangle {
            width: 10
            height: textbox.height
            color: "#ffffff"
        }
        TextBox {
            id: textbox
            fontSize: text_proto.font.pointSize
            textBoxHeight: text_proto.height
            textBoxWidth: text_proto.width + 16
            focus: true
            font: text_proto.font
            inputMask: "HH HH HH HH . HH HH HH HH"
            Connections {
                onTextChanged: rect.rowChanged(text.replace(/[ .]/g, ''))
            }
        }

        Rectangle {
            width: 10
            height: textbox.height
            color: "#ffffff"
        }
        Rectangle {
            width: 30
            color: "#ffffff"
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 0
            anchors.top: parent.top
            anchors.topMargin: 0

            Rectangle {
                width: text1.width + 10
                height: 20
                color: "#000000"
                anchors.verticalCenter: parent.verticalCenter
                anchors.horizontalCenter: parent.horizontalCenter

                Text {
                    id: text1
                    color: "#ffffff"
                    text: name
                    anchors.horizontalCenter: parent.horizontalCenter
                    font.pixelSize: 15
                    transformOrigin: Item.Center
                    anchors.verticalCenter: parent.verticalCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
        }
    }

    TextInput {
        id: text_proto
        visible: false
        font.pointSize: 15
        font.family: "Consolas"
        font.capitalization: Font.AllUppercase
        text: qsTr("ff ff ff ff . ff ff ff ff")

    }
}
