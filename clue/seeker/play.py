from django.db import models
from django.contrib.auth.models import *
from seeker.models import *
from django.http import HttpResponse, HttpResponseRedirect
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.utils.safestring import SafeString
from django.utils import simplejson
from lobby.models import *
from lobby import *
from games import *
from lb.util import expand, serialize_qs

@login_required
@render_to('game.html')
def game(request, game_id):
    #404 for invalid game
    game = get_object_or_404(Game, id=game_id)
    bg = BoardGame(game)
    #404 if user is not a player in game
    player = Player.objects.select_related('user', 'cell').get(user=request.user, game=game)
    turn = Turn(
        player = player
    )

    if request.method == 'POST':
        bg.move_for_cpus()
        game_dict = bg.serialize(player)
        
        remaining = player.remaining_guesses()
        game_dict['remaining_guesses'] = remaining
        print player, remaining
        
        if 'move' in request.POST:
            move_coords = request.POST['move']
            x, y = move_coords.split(',')

            print "NEW LOCATION %s , %s" % (x, y)
            print "PLAYER LOCATION %s , %s" % (player.x, player.y)
                
            
            cells = game.get_player_cells_within(int(x), int(y), 0)
            if cells:
               
                direction = player.get_direction_of_movement(x, y)
                print "DIRECTION: %s" % direction

                cubicle = cells[0]
                cubicle_owner = cubicle.player
                #if(cubicle_owner.id == player.id):
                #    if (direction == "down" or direction == "right"):
                #        print "VALID"
                #        
                #        new_clue = player.investigate_cell(cubicle)
                #        if new_clue:
                #            game_dict['new_clue'] = new_clue.serialize()
                #    else:
                #        print "INVALID"
                #        x = player.x
                #        y = player.y
                #else:
                #    if (direction == "up" or direction == "right"):
                #        print "VALID"
                #        
                #        new_clue = player.investigate_cell(cubicle)
                #        if new_clue:
                #            game_dict['new_clue'] = new_clue.serialize()
                #    else:
                #        print "INVALID"
                #        x = player.x
                #        y = player.y

                new_clue = player.investigate_cell(cubicle)
                if new_clue:
                    game_dict['new_clue'] = new_clue.serialize()
                    
            try:
                player.move_to(x, y)
                turn.action = 'move'
                turn.params = move_coords
                game_dict = bg.serialize(player)
            except ValueError:
                print "Too late move: %s" % (move_coords)
            
        if 'investigate' in request.POST:
            investigating_player_id = request.POST['investigate']
            investigating_player = Player.objects.get(id=investigating_player_id, game=game)
            new_clue = player.investigate(investigating_player)
            if new_clue:
                game_dict['new_clue'] = new_clue.serialize()
            
            turn.action = 'investidate'
            turn.params = investigating_player_id
            
        if 'guess' in request.POST:
            user_id, role_id = request.POST['guess'].split('=')
            user = User.objects.get(id=user_id)
            role = Role.objects.get(id=role_id)
            new_clue = bg.guess(request.user, user, role)
            game_dict['new_clue'] = new_clue.serialize()
        
            turn.action = 'guess'
            turn.params = request.POST['guess']
            
            if player.can_guess_without_deduction():
                game.is_current = False
                game.end = datetime.now()
                game.save()
                game_dict = expand(game)
                
        if turn.action:
            turn.save()
        
        return HttpResponse(simplejson.dumps(game_dict), content_type='application/json')
        
    context = {
        'game': game,
        'player': player,
        'board_html': SafeString(bg.html(request))
    }

    return context

@render_to('clues.html')
def clues(request, game_id):
    game = Game.objects.get(id=game_id)
    player = get_object_or_404(Player,
        user = request.user,
        game = game
    )
    context = {
        'player': player,
        'game': game
    }

    return context


@render_to('guesser.html')
def guesser(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    
    if not game.is_current:
        return HttpResponseRedirect('/seeker/game/%s/' % game.id)
    
    player = get_object_or_404(Player,
        user = request.user,
        game = game
    )
    other_player = Player.objects.get(id=request.POST['player'])

    known_facts = player.clue_set.filter(fact__neg=False).values('fact__player')
    correct_guesses = player.guess_set.filter(correct=True).values('other_player')
    roles = PlayerRole.objects.filter(player__in=game.player_set.all()).exclude(player__in=known_facts).exclude(player__in=correct_guesses)
    other_players = game.player_set.exclude(id__in=known_facts)

    context = {
        'game'  : game,
        'player': player,
        'roles' : roles,
        'other_player': other_player,
        'other_players': other_players
    }
    return context

def guess(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    player = Player.objects.get(
        user = request.user,
        game = game
    )
    other_player = Player.objects.get(id=request.POST['player'])
    role = Role.objects.get(id=request.POST['role'])
    cell = PlayerCell.objects.get(id=request.POST['cell'])
    
    guess = Guess(
        player = player,
        other_player = other_player,
        role = role,
        cell = cell,
    )
    
    print "Guessing:", other_player.user.username
    print guess.other_player.playerrole.role, role
    print guess.other_player.playercell, cell
    
    if guess.other_player.playerrole.role == role and guess.other_player.playercell == cell: guess.correct = True
    else: guess.correct = False
    
    guess.save()
    
    return HttpResponse(simplejson.dumps(expand(guess)))

def _guess(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    guesses_str = request.REQUEST['guess']
    guesses = guesses_str.split(',')
    print guesses

    player = Player.objects.get(
        user = request.user,
        game = game
    )
    try:
        submission = Submission.objects.get(player=player)
    except:
        submission = Submission(
            player = player,
            game = game
        )
        submission.save()
    
    try:
        #lb - for debugging, in reality you shouldn't get to guess more than once
        submission.roleguess_set.all().delete()
    except:
        pass

    for guess in guesses:
        (other_player_id, role_id) = guess.split('=')
        other_player = Player.objects.get(id=other_player_id)
        role = Role.objects.get(id=role_id)
        
        guess = RoleGuess(
            other_player = other_player,
            role = role,
            submission = submission
        )
        
        guess.role = role
        guess.save()
    
    from seeker.games import BasicRoleGame
    brg = BasicRoleGame(game)
    brg.check_submission(submission)
    return HttpResponse("")
    
def guess_for_cpus(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    cpu_players = game.player_set.filter(user__is_active=False).all()
    
    from seeker.games import BasicRoleGame
    brg = BasicRoleGame(game)
    
    for player in cpu_players:
        other_players = game.player_set.exclude(user=player.user).all()
        roles = PlayerRole.objects.filter(player__in=game.player_set.all()).exclude(role=player.playerrole.role)
        
        try:
            submission = Submission.objects.get(player=player)
        except:
            submission = Submission(
                player = player,
                game = game
            )
            submission.save()
                
        try:
            #lb - for debugging, in reality you shouldn't get to guess more than once
            submission.roleguess_set.all().delete()
        except:
            pass
        
        for other_player in other_players:
            role = roles[0]
            roles = roles[:1]
            guess = RoleGuess(
                other_player = other_player,
                role = role.role,
                submission = submission
            )
            guess.save()
    
        brg.check_submission(submission)
            
    return HttpResponse("")
            
    
def quit(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    player = Player.objects.get(
        user = request.user,
        game = game,
        is_current = True,
    )
    player.is_current = False
    player.save()
    return HttpResponseRedirect('/lobby/home/')

@render_to('notification.html')
def show_notification(request, text):
    text = text.replace("_", " ")
    return {"text" : text}
    
