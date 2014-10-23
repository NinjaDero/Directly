from Directly import Ext

@Ext.cls
class Store():
    @staticmethod
    @Ext.method
    def get_dummy_data(request, data):
        # Create dummy data to fill our dummy store.
        # It's just to show how to load a store using Directly.

        # Please take a look at your console and see how 'data' looks!
        # Stores usually just send an object/dict instead of multiple arguments
        print data
        dummy = []
        for i in range(10):
            dummy.append({'id': i})

        return dummy