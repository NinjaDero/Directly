from Directly import Ext

@Ext.cls
class Buttons():
    @staticmethod
    @Ext.method
    def ping(request):
        return "Pong!"

    @staticmethod
    @Ext.method
    def reverse(request, text):
        return text[::-1]

    @staticmethod
    @Ext.method
    def full_caps(request, text):
        all_caps = Buttons.make_caps(text)
        return all_caps

    @staticmethod
    @Ext.method
    def full_lows(request, text):
        all_lows = Buttons.make_lows(text)
        return all_lows


    # Not included, remains hidden to Ext.direct.Manager
    # You don't have to separate your exposed and hidden methods, if you don't want to.
    # They can also not be called if the Manager is edited manually
    @staticmethod
    def make_caps(_text):
        if 'upper' in dir(_text):
            _text = _text.upper()
        return _text

    @staticmethod
    def make_lows(_text):
        if 'lower' in dir(_text):
            _text = _text.lower()
        return _text