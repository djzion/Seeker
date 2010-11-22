
Lobby = {
    id: null,
    
    //Call from view after id is set
    init: function()
    {
        this.updateMembers()
        this._update_members = new PeriodicalExecuter(Lobby.updateMembers, 2)
    },
    
    updateMembers: function()
    {
        new Ajax.Request('/lobby/get_lobby/', {
            parameters: {'lobby': Lobby.id},
            onSuccess: function(resp)
            {
                data = resp.responseText.evalJSON()
                if (data['game']) document.location = '/seeker/game/' + data['game']
                Lobby.members = data['members']
                Lobby._drawMembers()
            }
        })   
    },
    
    updateMessages: function()
    {
        new Ajax.Request('/lobby/messages/get/', {
            parameters: {'lobby': Lobby.id},
            onSuccess: function(resp)
            {
                data = resp.responseText.evalJSON()
                Lobby.messages = data
                Lobby._drawMessages()
            }
        })
    },
    
    _drawMessages: function()
    {
        $("messages").update("")
        Lobby.messages.each(function(msg)
        {
            h = "<b>" + msg.sender.username + "</b> at " + msg.created + "<br/>"
            h += "<p>" + msg.content + "</p>"
            $('messages').innerHTML += h
            
        })
    },
    
    _drawMembers: function()
    {
        $('members').update("")
        //$('id_to').update("")
        
        Lobby.members.each(function(member)
        {
            
            h = "<li><b>" + member.user.username + "</b>"
            h += " at " + member.created;
            if (member.user.id != User.id) {
                h += " <a href='javascript: Lobby.removeUser("+ member.id +")'>x</a></li>";
            }
            
            $('members').innerHTML += h
            
            //$('id_to').innerHTML += '<option value="' + member.user.id + '">' + member.user.username + '</option>'
        });
    },
    
    addCpuUser: function()
    {
        new Ajax.Request('/lobby/members/add_cpu_user/', {
            parameters: {'lobby': Lobby.id},
            onSuccess: function(resp)
            {
                
            }
        })
    },
    
    removeUser: function(member_id)
    {
        new Ajax.Request('/lobby/members/remove_member/', {
            parameters: {'member_to_remove': member_id},
            onSuccess: function(resp)
            {
                
            }
        })
    },
    
    inviteMember: function()
    {
        new Ajax.Request('/lobby/members/invite/', {
            parameters: {'lobby': Lobby.id, 'email': $('email').value},
            onSuccess: function(resp)
            {
                
            }
        })  
    }
}

//update_messages = new PeriodicalExecuter(Lobby.updateMessages, 2)