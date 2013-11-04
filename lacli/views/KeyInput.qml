import QtQuick 1.1


Column {
    id: column1
    spacing: 20
    IdRow { }
    property alias button: button1
    property alias model: mymodel


    ListView {

        boundsBehavior: Flickable.StopAtBounds
        id: list
        width: 300
        height: 200
        contentHeight: list.height
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

    Button {
        id: button1
        text: "Decrypt"
        signal rowChanged()
        onRowChanged: {
            enabled = true
            for (var i=0; i< mymodel.count; i++) {
                if (!mymodel.get(i).complete)
                    enabled = false
            }


        }
    }

}
