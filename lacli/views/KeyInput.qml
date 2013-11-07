import QtQuick 1.1


Column {
    id: column1
    spacing: 20
    IdRow { visible: false }
    property alias button: button1
    property alias model: mymodel
    property alias folder: text_input1.text


    ListView {

        boundsBehavior: Flickable.StopAtBounds
        id: list
        x: 0
        width: 300
        height: 200
        contentHeight: 166
        contentWidth: list.width
        focus: true

        spacing: 30
        delegate: KeyRow {
            id: foo
            Connections {
                onAcceptableChanged: {
                    mymodel.setProperty(index, 'complete', foo.acceptable)
                    button1.rowChanged()
                    if (foo.acceptable)
                        list.incrementCurrentIndex()
                }

                onRowChanged: {
                    mymodel.setProperty(index, 'value', val)
                }
            }}
        model: ListModel {
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
    }
Row{
    Rectangle {
        width: text_input1.width
        height: text_input1.height
        color: "#dbd6d6"
        smooth: true
        border.color: "#000000"
        TextInput {
            id: text_input1
            width: 200
            height: 22
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            focus: true
            font.pointSize: 12
            onTextChanged: button1.rowChanged()
        }
        border.width: 1
    }

    Button {
        id: button2
        text: "Browse"
        enabled: true
        Connections {
            onButtonClicked: text_input1.text = destsel.getDirectory()
        }
        font.pixelSize: 10
        radius: 0
    }
}

    Button {
        id: button1
        text: "Decrypt"
        signal rowChanged()
        x: 39
        onRowChanged: {
            enabled = destsel.dirExists(text_input1.text)
            for (var i=0; i< mymodel.count; i++) {
                if (!mymodel.get(i).complete)
                    enabled = false
            }
        }
    }

}
