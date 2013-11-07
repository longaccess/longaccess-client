import QtQuick 1.1

Rectangle {
    id: rectangle1
    width: column1.width
    height: column1.height

    color: "#ffffff"
    signal decrypt(string key, string path)
    property alias folder: key_input.folder
    Column {
        id: column1
        x: 0
        y: 0
        spacing: 10
        Text {
            text: "Please input the key from your certificate:"
        }
        KeyInput {
            id: key_input
        }
        MouseArea {
            id: mousearea1
            width: 100
            height: 100

        }
    }

    Connections {
        target: key_input.button
        onButtonClicked: {
            var key=''
            for (var i=0; i<key_input.model.count; i++) {
                key += key_input.model.get(i).value
            }
            rectangle1.decrypt(key, folder)
            Qt.quit()

        }
    }
}