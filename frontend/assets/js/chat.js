var checkout = {};



$(document).ready(function() {

  function generateSessionId(length = 16) {
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let sessionId = '';
    for (let i = 0; i < length; i++) {
      const randomIndex = Math.floor(Math.random() * characters.length);
      sessionId += characters[randomIndex];
    }
    return sessionId;
  }

  
  // console.log(saved_session_data)
  let saved_session_data = "";
  let sessionId = "";

  var $messages = $('.messages-content'),
    d, h, m,
    i = 0;

  $(window).load(function() {
    $messages.mCustomScrollbar();
    // Get sessionId if it exists, and then make a api call with dummy message.
    // We load or generate session-id
    sessionId = Cookies.get('Session-ID') || generateSessionId();
    Cookies.set('Session-ID', sessionId);
    sdk.sessionGet({
      "sessionId": sessionId
    }).then(response => {
      saved_session_data = response.data.saved_session;
      if(!saved_session_data) {
        insertResponseMessage('Hi there, I\'m your personal Concierge. How can I help?');
      } else {
        insertResponseMessage('Welcome Back! <br>Would you like to get more recommendations based on your previous search : ' 
          + saved_session_data + " ?"
        );
      }
    })
  });

  function updateScrollbar() {
    $messages.mCustomScrollbar("update").mCustomScrollbar('scrollTo', 'bottom', {
      scrollInertia: 10,
      timeout: 0
    });
  }

  function setDate() {
    d = new Date()
    if (m != d.getMinutes()) {
      m = d.getMinutes();
      $('<div class="timestamp">' + d.getHours() + ':' + m + '</div>').appendTo($('.message:last'));
    }
  }

  function callChatbotApi(message, id) {
    // params, body, additionalParams
    return  sdk.chatbotPost({
      "Session-ID": id
    }, {
      messages: [{
        type: 'unstructured',
        unstructured: {
          text: message
        }
      }]
    }, {}
    );
  }

  function isYes(message) {
    return ["yes", "y", "sure", "ok", "okay"].includes(message.trim().toLowerCase());
  }

  function insertMessage() {
    msg = $('.message-input').val();
    if ($.trim(msg) == '') {
      return false;
    }
    $('<div class="message message-personal">' + msg + '</div>').appendTo($('.mCSB_container')).addClass('new');
    setDate();
    $('.message-input').val(null);
    updateScrollbar();

    if(saved_session_data) {
      if(isYes(msg)) {
        insertResponseMessage("Great! I shall email you some suggestions soon.");
        // Make POST request to push to queue
        sdk.sessionPost({
        },{
          "sessionId": sessionId
        },{}).then(response => {
          console.log(response.data.saved_session);
        }).catch(err => {
          console.log(err);
        })
      } else {
        sessionId = generateSessionId();
        Cookies.set('Session-ID', sessionId);
        console.log(`New sessionId: ${sessionId}`);
        insertResponseMessage("Ok! Let's start a new session then. What would you like to do ?");
      }
      return;
    }
    callChatbotApi(msg, sessionId)
      .then((response) => {
        console.log(response);
        var data = response.data;

        if (data.messages && data.messages.length > 0) {
          console.log('received ' + data.messages.length + ' messages');

          var messages = data.messages;

          for (var message of messages) {
            if (message.type === 'unstructured') {
              insertResponseMessage(message.unstructured.text);
            } else if (message.type === 'structured' && message.structured.type === 'product') {
              var html = '';

              insertResponseMessage(message.structured.text);

              setTimeout(function() {
                html = '<img src="' + message.structured.payload.imageUrl + '" witdth="200" height="240" class="thumbnail" /><b>' +
                  message.structured.payload.name + '<br>$' +
                  message.structured.payload.price +
                  '</b><br><a href="#" onclick="' + message.structured.payload.clickAction + '()">' +
                  message.structured.payload.buttonLabel + '</a>';
                insertResponseMessage(html);
              }, 1100);
            } else {
              console.log('not implemented');
            }
          }
        } else {
          insertResponseMessage('Oops, something went wrong. Please try again.');
        }
      })
      .catch((error) => {
        console.log('an error occurred', error);
        insertResponseMessage('Oops, something went wrong. Please try again.');
      });
  }

  $('.message-submit').click(function() {
    insertMessage();
  });

  $(window).on('keydown', function(e) {
    if (e.which == 13) {
      insertMessage();
      return false;
    }
  })

  function insertResponseMessage(content) {
    $('<div class="message loading new"><figure class="avatar"><img src="https://media.tenor.com/images/4c347ea7198af12fd0a66790515f958f/tenor.gif" /></figure><span></span></div>').appendTo($('.mCSB_container'));
    updateScrollbar();

    setTimeout(function() {
      $('.message.loading').remove();
      $('<div class="message new"><figure class="avatar"><img src="https://media.tenor.com/images/4c347ea7198af12fd0a66790515f958f/tenor.gif" /></figure>' + content + '</div>').appendTo($('.mCSB_container')).addClass('new');
      setDate();
      updateScrollbar();
      i++;
    }, 500);
  }

});
