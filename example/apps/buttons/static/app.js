/*

This is a basic example of how to use Directly and how *I* use it.
I suggest using debug=True to see what kind of data your store sends and apply that logic to your backend

 */
Ext.define('DirectlyExamplePanel', {
    extend: 'Ext.panel.Panel',

    floating: true,
    modal: true,
    title: 'Directly Examples',
    itemId: 'panel-frame',
    autoShow: true,

    layout: {
        type: 'table',
        columns: 2
    },
    bodyPadding: 5,

    defaults: {
        xtype: 'panel',
        width: 200,
        height: 280,
        padding: 5
    },

    initComponent: function() {
        var me = this;
        this.items = [
            {
                title: 'SimpleButtons',
                bodyPadding: 2,
                defaults: {
                    width: '100%'
                },
                items: [
                    {
                        xtype: 'button',
                        text: 'Ping',
                        handler: this.ping
                    },
                    {
                        xtype: 'button',
                        text: 'Reverse Notepad',
                        handler: function(btn) {
                            me.notepadAction(btn, 'reverse')
                        }
                    },
                    {
                        xtype: 'button',
                        text: 'Notepad all-caps',
                        handler: function(btn) {
                            me.notepadAction(btn, 'full_caps')
                        }
                    },
                    {
                        xtype: 'button',
                        text: 'Notepad all-lower',
                        handler: function(btn) {
                            me.notepadAction(btn, 'full_lows')
                        }
                    }
                ]
            },
            {
                title: 'Notepad',
                layout: 'fit',
                listeners: {
                    boxready: me.loadNotepad
                },
                items: [
                    {
                        xtype: 'textarea',
                        itemId: 'example-textbox'
                    }
                ],
                tools: [
                    {
                        type: 'save',
                        callback: me.saveNotepad
                    },
                    {
                        type: 'refresh',
                        callback: me.loadNotepad
                    }
                ]
            }
        ];

        this.callParent();
    },


    // Calls start HERE!
    // Direct methods can take a callback function after all arguments
    // If your function doesn't have any parameters, the callback is the first argument


    ping: function() {
        var t = new Date().getTime();
        Example.Buttons.ping(function(answer) {
            var time = new Date().getTime() - t;
            Ext.toast({
                html: '<center>' + answer + '<br/>Time taken: ' + time + 'ms</center>',
                closable: false,
                width: 400
            });
        });
    },

    // I reuse the same function, since it's basically the same action - modify string and return it.
    // I am accessing the methods using a String, since you can access an objects properties using "object['key']"
    notepadAction: function(component, action) {
        var notepad = component.up('#panel-frame').down('#example-textbox');
        var text = notepad.getValue();
        Example.Buttons[action](text, function(newText) {
            notepad.setValue(newText);
        });
    },


    saveNotepad: function(panel) {
        var text = panel.down('#example-textbox').getValue();
        Example.Notepad.write_file(text, function(success) {
            Ext.toast({
                html: '<center>' + (success ? 'saved' : 'failed') + '</center>',
                closable: false,
                width: 400
            });
        });
    },

    loadNotepad: function(panel) {
        var text = panel.down('#example-textbox').getValue();
        Example.Notepad.read_file(function(text, success) {
            Ext.toast({
                html: '<center>' + (success ? 'loaded' : 'failed') + '</center>',
                closable: false,
                width: 400
            });
            if (success) {
                panel.down('#example-textbox').setValue(text);
            }
        });
    }
});



Ext.onReady(function() {
    Ext.create('Ext.Viewport', {
        items: [
            Ext.create('DirectlyExamplePanel')
        ]
    });

    // Dummy store. Loads data, displays a toast and that's it.
    var store = Ext.create('Ext.data.Store', {
        fields: ['id'],
        autoLoad: true,
        proxy: {
            type: 'direct',
            directFn: 'Example.Store.get_dummy_data',
            reader: {
                type: 'json'
            },
            extraParams: {
                foo: 'bar'
            }
        },
        listeners: {
            load: function(store, records) {
                Ext.toast({
                    html: '<center>Loaded ' + records.length + ' dummy-records</center>',
                    closable: false,
                    width: 400
                });
            }
        }
    })
});