import QtQuick 1.1
FocusScope {
    property bool complete: false
    property bool acceptable: text_input1.acceptableInput
    property string val: text_input1.text.replace(/[ .]/g, '')
    height: text_input1.height
    signal rowChanged()
    Grid {
        id: row1
        anchors.fill: parent
        columns: 2
        rows: 1
        spacing: 10
        height: 50
        Rectangle {
            x: 0
            y: 0
            width: text1.width + 10
            height: text_input1.height+5
            color: "#000000"
            radius: 99
            border.width: 1
            border.color: "#000000"

            Text {
                id: text1
                x: 8
                y: 0
                color: "#ffffff"

                text: name
                anchors.verticalCenterOffset: 0
                anchors.horizontalCenterOffset: 0
                anchors.topMargin: 0
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                anchors.top: parent.top
                font.pointSize: 11
                verticalAlignment: Text.AlignVCenter
            }
        }
        Rectangle {
            width: text_input1.width +5
            height: text_input1.height+5
            color: "#dbd6d6"
            border.width: 1
            border.color: "#000000"

            TextInput {
                id: text_input1
                focus: true
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                font.pointSize: 12
                font.family: "Consolas"
                inputMask: "HH HH HH HH . HH HH HH HH"

            }
        }
    }
    Connections {
        target: text_input1
        onTextChanged: rowChanged()
    }
}
