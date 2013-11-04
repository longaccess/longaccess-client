import QtQuick 1.1
FocusScope {
    width: row1.width
    height: row1.height
    Grid {
        id: row1
        columns: 2
        rows: 1
        spacing: 10
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

                text: "A"
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
            color: "#00000000"

            Text {
                id: text_input1
                focus: true
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                font.pointSize: 12
                font.family: "Consolas"
                text: "your key id"

            }
        }
    }
}
