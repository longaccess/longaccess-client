import QtQuick 1.1


Column {
    id: keyinput
    signal decrypt(string key, string path)
    property bool hasError: false
    transformOrigin: Item.Center

    spacing: 20

    ListModel {
        id: mymodel
        ListElement {
            name: "B"
            complete: false
            value: ""
        }
        ListElement {
            name: "C"
            complete: false
            value: ""
        }
        ListElement {
            name: "D"
            complete: false
            value:""
        }
        ListElement {
            name: "E"
            complete: false
            value:""
        }
    }

    Component {
        id: _error_msg
        Column {
            Text {
                color: "#ff0000"
                text: "Error"
                anchors.right: parent.right
                anchors.rightMargin: 0
                font.pointSize: 15
            }
            Text {
                color: "#992626"
                text: "please try again"
                font.pointSize: 9
                font.family: "Open Sans"
                verticalAlignment: Text.AlignVCenter
            }
        }
    }

    Row {
        height: 1
        anchors.right: parent.right
        anchors.rightMargin: 0
        anchors.left: parent.left
        anchors.leftMargin: 0
    }

    Row {
        anchors.horizontalCenter: parent.horizontalCenter
        Text {
            id: list_title
            text: "Enter Certificate Key"
            font.family: "Arial"
            font.bold: true
            font.pixelSize: 19
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
        }
    }
    Row {
        id: key_row
        Column {
            id: column1
            spacing: 10

            Repeater {
                id: list
                focus: true
                model: mymodel
                onItemAdded: {
                    if (!index) {
                        item.forceActiveFocus()
                    }
                }

                delegate: KeyRow {
                    id: foo
                    Connections {
                        onAcceptableChanged: {
                            mymodel.setProperty(index, 'complete', foo.acceptable)
                            button1.rowComplete()
                            if (foo.acceptable)
                                if (index + 1 < list.count)
                                    list.itemAt(index+1).forceActiveFocus()
                                else
                                    folder.forceActiveFocus()
                                keyinput.hasError = false
                        }

                        onRowChanged: {
                            mymodel.setProperty(index, 'value', val)
                        }
                    }
                }
            }
        }
    }
    Row{
        id: folder_row
        anchors.right: parent.right
        anchors.rightMargin: 10
        layoutDirection: Qt.RightToLeft
        spacing: 10


        Button {
            id: button2
            text: "Browse"
            enabled: true
            Connections {
                onButtonClicked: folder.text = destsel.getDirectory()
            }
            font.pixelSize: 10
            radius: 0
        }

        TextBox {
            id: folder
            anchors.verticalCenter: parent.verticalCenter
            fontSize: 12
            textBoxHeight: 20
            textBoxWidth: 150
            focus: true
            font.pointSize: 12
            Connections {
                onTextChanged: button1.folderChanged()
            }

        }

        Rectangle {
            id: rectangle1
            width: childrenRect.width
            height: childrenRect.height
            color: "#ffffff"
            anchors.verticalCenter: parent.verticalCenter
            z: -2

            Text {
                id: text1
                text: qsTr("Folder:")
                font.pointSize: 12
            }
        }
    }


    Row {
        id: button_row
        layoutDirection: Qt.RightToLeft
        anchors.right: parent.right
        anchors.rightMargin: 10
        anchors.left: parent.left
        anchors.leftMargin: 10
        spacing: 10
        Button {
            id: button1
            text: "Decrypt"
            signal rowComplete()
            signal folderChanged()
            onRowComplete: {
                enabled = destsel.dirExists(folder.text)
                for (var i=0; i< mymodel.count; i++) {
                    if (!mymodel.get(i).complete)
                        enabled = false
                }
            }
            onFolderChanged: {
                if (destsel.dirExists(folder.text))
                    rowComplete()
            }

            onButtonClicked: {
                var key=''
                for (var i=0; i<list.model.count; i++)
                    key += list.model.get(i).value
                keyinput.decrypt(key, folder.text)
                if(!keyinput.hasError)
                    Qt.quit()
            }
        }
        Button {
            id: button3
            text: "Cancel"
            enabled: true
            onButtonClicked: Qt.quit()
        }
        Loader {
            sourceComponent: _error_msg
            id: error
            opacity: 0
        }
    }

    Row {
        height: 1
        anchors.right: parent.right
        anchors.rightMargin: 0
        anchors.left: parent.left
        anchors.leftMargin: 0
    }
    states: [
        State {
            when: keyinput.hasError
            PropertyChanges {
                target: error
                opacity: 1
            }
        }
    ]

}

