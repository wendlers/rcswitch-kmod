var swsrv = {

    setBaseUrl: function(aBaseUrl)
    {
        this.baseUrl = aBaseUrl;
    },

    sendCommand: function(address, channel, state)
    {
         $.mobile.loading("show");

         $.ajax({
            url: this.baseUrl + '/switch/' + address + '/' + channel,
            type: 'POST',
            data: { 'state': state },
            error : function (xhr, status, text) {
              $.mobile.loading("hide");
              swsrv.showServerError();
            },
            success: function (data) {
                $.mobile.loading("hide");
            }
        });
    },

    showServerError: function()
    {
        $("#serverError").popup("open");
    },
};